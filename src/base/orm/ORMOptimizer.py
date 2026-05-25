import sys
import logging

logging.basicConfig(level=logging.INFO)

try:
    import psycopg2
    from psycopg2 import pool
    PSYCOPG_VERSION = 2
    print("✓ ORMOptimizer: Используем psycopg2 с модулем pool")
except ImportError:
    try:
        import psycopg
        PSYCOPG_VERSION = 3
        print("✓ ORMOptimizer: Используем psycopg (v3) с кастомным pool")
        
        class SimpleConnectionPool:
            def __init__(self, minconn, maxconn, **kwargs):
                self.minconn = minconn
                self.maxconn = maxconn
                self.kwargs = kwargs
                self._pool = []
                self._used = []
                self._lock = threading.RLock()
                
                for _ in range(minconn):
                    conn = psycopg.connect(**kwargs)
                    self._pool.append(conn)
            
            def getconn(self, timeout=None):
                with self._lock:
                    if self._pool:
                        conn = self._pool.pop()
                    else:
                        if len(self._used) < self.maxconn:
                            conn = psycopg.connect(**self.kwargs)
                        else:
                            raise pool.PoolError("Нет доступных соединений в пуле")
                    self._used.append(conn)
                    return conn
            
            def putconn(self, conn, close=False):
                with self._lock:
                    if close:
                        conn.close()
                    elif conn in self._used:
                        self._used.remove(conn)
                        if len(self._pool) < self.maxconn:
                            self._pool.append(conn)
                        else:
                            conn.close()
            
            def closeall(self):
                with self._lock:
                    for conn in self._pool + self._used:
                        try:
                            conn.close()
                        except:
                            pass
                    self._pool.clear()
                    self._used.clear()
        
        class PoolModule:
            ThreadedConnectionPool = SimpleConnectionPool
            PoolError = Exception
        
        pool = PoolModule()
        
    except ImportError:
        try:
            import psycopg_binary as psycopg
            PSYCOPG_VERSION = 3
            print("✓ ORMOptimizer: Используем psycopg_binary (v3) с кастомным pool")
            
            class SimpleConnectionPool:
                def __init__(self, minconn, maxconn, **kwargs):
                    self.minconn = minconn
                    self.maxconn = maxconn
                    self.kwargs = kwargs
                    self._pool = []
                    self._used = []
                    self._lock = threading.RLock()
                    
                    for _ in range(minconn):
                        conn = psycopg.connect(**kwargs)
                        self._pool.append(conn)
                
                def getconn(self, timeout=None):
                    with self._lock:
                        if self._pool:
                            conn = self._pool.pop()
                        else:
                            if len(self._used) < self.maxconn:
                                conn = psycopg.connect(**self.kwargs)
                            else:
                                raise Exception("Нет доступных соединений в пуле")
                        self._used.append(conn)
                        return conn
                
                def putconn(self, conn, close=False):
                    with self._lock:
                        if close:
                            conn.close()
                        elif conn in self._used:
                            self._used.remove(conn)
                            if len(self._pool) < self.maxconn:
                                self._pool.append(conn)
                            else:
                                conn.close()
                
                def closeall(self):
                    with self._lock:
                        for conn in self._pool + self._used:
                            try:
                                conn.close()
                            except:
                                pass
                        self._pool.clear()
                        self._used.clear()
            
            class PoolModule:
                ThreadedConnectionPool = SimpleConnectionPool
                PoolError = Exception
            
            pool = PoolModule()
            
        except ImportError:
            raise ImportError("ORMOptimizer: Нет драйвера PostgreSQL!")

import threading
from typing import Any, Dict
from contextlib import contextmanager
from datetime import datetime
import time
import atexit


class ConnectionPool:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self, 
                 min_conn: int = 2,
                 max_conn: int = 20,
                 idle_timeout: int = 300,
                 max_lifetime: int = 3600):
        if not hasattr(self, '_initialized'):
            self.min_conn = min_conn
            self.max_conn = max_conn
            self.idle_timeout = idle_timeout
            self.max_lifetime = max_lifetime
            self._pools: Dict[str, pool.ThreadedConnectionPool] = {}
            self._pool_metrics: Dict[str, Dict] = {}
            self._stats_lock = threading.RLock()
            self._cleanup_thread = None
            self._shutdown = False
            self._initialized = True
            
            self._start_cleanup_thread()
            atexit.register(self.close_all)
    
    def get_pool(self, db_params: Dict[str, str]) -> pool.ThreadedConnectionPool:
        if PSYCOPG_VERSION == 3:
            pg_params = db_params.copy()
            if 'database' in pg_params and 'dbname' not in pg_params:
                pg_params['dbname'] = pg_params.pop('database')
                logging.debug(f"Нормализовал параметры для psycopg 3: {pg_params}")
        else:
            pg_params = db_params
        
        pool_key = self._get_pool_key(pg_params)
        
        with self._stats_lock:
            if pool_key not in self._pools:
                logging.info(f"Создаю новый пул соединений для {pool_key}")
                
                try:
                    pg_pool = pool.ThreadedConnectionPool(
                        minconn=self.min_conn,
                        maxconn=self.max_conn,
                        **pg_params 
                    )
                    
                    self._pools[pool_key] = pg_pool
                    
                    self._pool_metrics[pool_key] = {
                        'created_at': datetime.now(),
                        'total_connections_created': 0,
                        'connections_checked_out': 0,
                        'connections_returned': 0,
                        'pool_errors': 0,
                        'last_health_check': datetime.now(),
                        'connections': {}
                    }
                    
                    self._warmup_pool(pg_pool, pg_params)
                    
                except Exception as e:
                    logging.error(f"Ошибка создания пула соединений: {e}")
                    raise
            
            return self._pools[pool_key]
    
    def _get_pool_key(self, db_params: Dict[str, str]) -> str:
        host = db_params.get('host', 'localhost')
        port = db_params.get('port', '5432')

        dbname = db_params.get('dbname') or db_params.get('database', 'postgres')
        return f"{host}:{port}/{dbname}"
    
    def _warmup_pool(self, pg_pool: pool.ThreadedConnectionPool, db_params: Dict[str, str]):
        connections = []
        try:
            for _ in range(self.min_conn):
                conn = pg_pool.getconn()
                connections.append(conn)
                
                with self._stats_lock:
                    pool_key = self._get_pool_key(db_params)
                    if pool_key in self._pool_metrics:
                        self._pool_metrics[pool_key]['total_connections_created'] += 1
                        
        except Exception as e:
            logging.warning(f"Ошибка при предварительном создании соединений: {e}")
        finally:
            for conn in connections:
                try:
                    pg_pool.putconn(conn)
                except:
                    pass
    
    @contextmanager
    def get_connection(self, db_params: Dict[str, str], timeout: int = 30):
        pool_key = self._get_pool_key(db_params)
        pool_obj = self.get_pool(db_params)
        conn = None
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                try:
                    conn = pool_obj.getconn(timeout=1)
                    if conn:
                        break
                except:
                    time.sleep(0.1)
            
            if not conn:
                raise TimeoutError(f"Не удалось получить соединение из пула за {timeout} секунд")
            
            with self._stats_lock:
                if pool_key in self._pool_metrics:
                    self._pool_metrics[pool_key]['connections_checked_out'] += 1
                    conn_id = id(conn)
                    if conn_id not in self._pool_metrics[pool_key]['connections']:
                        self._pool_metrics[pool_key]['connections'][conn_id] = datetime.now()
            
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            except:
                try:
                    pool_obj.putconn(conn, close=True)
                except:
                    pass
                conn = pool_obj.getconn()
            
            yield conn
            
        except Exception as e:
            logging.error(f"Ошибка получения соединения: {e}")
            raise
            
        finally:
            if conn:
                try:
                    pool_obj.putconn(conn)
                    with self._stats_lock:
                        if pool_key in self._pool_metrics:
                            self._pool_metrics[pool_key]['connections_returned'] += 1
                except Exception as e:
                    logging.error(f"Ошибка возврата соединения: {e}")
    
    def _start_cleanup_thread(self):
        def cleanup_worker():
            while not self._shutdown:
                try:
                    time.sleep(60)
                    self._cleanup_old_connections()
                except Exception as e:
                    logging.error(f"Ошибка в потоке очистки: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_old_connections(self):
        with self._stats_lock:
            for pool_key, pg_pool in list(self._pools.items()):
                try:
                    metrics = self._pool_metrics.get(pool_key, {})
                except Exception as e:
                    logging.error(f"Ошибка очистки пула {pool_key}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {}
        with self._stats_lock:
            for pool_key, pg_pool in self._pools.items():
                try:
                    metrics = self._pool_metrics.get(pool_key, {})
                    stats[pool_key] = {
                        'min_connections': self.min_conn,
                        'max_connections': self.max_conn,
                        'total_created': metrics.get('total_connections_created', 0),
                        'checked_out': metrics.get('connections_checked_out', 0),
                        'returned': metrics.get('connections_returned', 0),
                        'errors': metrics.get('pool_errors', 0),
                        'created_at': metrics.get('created_at'),
                        'last_health_check': metrics.get('last_health_check'),
                    }
                except Exception as e:
                    logging.error(f"Ошибка получения статистики: {e}")
        
        return stats
    
    def close_all(self):
        self._shutdown = True
        with self._stats_lock:
            for pool_key, pg_pool in self._pools.items():
                try:
                    pg_pool.closeall()
                    logging.info(f"Закрыт пул для {pool_key}")
                except Exception as e:
                    logging.error(f"Ошибка закрытия пула {pool_key}: {e}")
            
            self._pools.clear()
            self._pool_metrics.clear()
    
    def __del__(self):
        self.close_all()