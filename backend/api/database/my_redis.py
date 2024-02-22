import redis
import logging

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 示例配置，替换为你自己的配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# 创建并配置 Redis 连接池
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# 使用连接池创建 Redis 客户端实例
client = redis.Redis(connection_pool=pool)

def main():
    # 使用 Redis 执行命令
    client.set('my_key', 'Hello, Redis!')
    value = client.get('my_key')
    logger.info(f"Value: {value.decode('utf-8')}")

    # 获取 Redis 服务器信息并记录
    info = client.info()
    used_memory = info.get('used_memory_human', 'unknown')
    total_connections_received = info.get('total_connections_received', 'unknown')
    total_commands_processed = info.get('total_commands_processed', 'unknown')

    logger.info(f"Redis initialized. Used memory: {used_memory}, "
                f"Total connections received: {total_connections_received}, "
                f"Total commands processed: {total_commands_processed}")


