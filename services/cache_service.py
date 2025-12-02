import json
import os
import hashlib
from datetime import datetime, timedelta

CACHE_DIR = "cache/exercise_descriptions"
CACHE_TTL_DAYS = 7  # 缓存有效期7天

def _ensure_cache_dir():
    """确保缓存目录存在"""
    os.makedirs(CACHE_DIR, exist_ok=True)

def _get_cache_key(exercise_name, user_profile):
    """
    根据运动名称和用户资料生成缓存键。
    使用运动名称和用户资料的哈希（简化：使用用户ID和运动名称）
    """
    # 如果user_profile包含user_id，使用它；否则使用整个profile的JSON字符串哈希
    user_id = user_profile.get('user_id') if user_profile else None
    if user_id:
        key = f"{user_id}_{exercise_name}"
    else:
        # 如果没有user_id，使用profile的JSON表示（排序确保一致）
        # 首先确保profile可序列化
        serializable_profile = _make_json_serializable(user_profile) if user_profile else {}
        profile_str = json.dumps(serializable_profile, sort_keys=True)
        hash_obj = hashlib.md5(profile_str.encode())
        key = f"{hash_obj.hexdigest()}_{exercise_name}"
    # 文件名安全
    import re
    key = re.sub(r'[^\w\-_]', '_', key)
    return key

def get_cached_description(exercise_name, user_profile):
    """获取缓存的运动介绍，如果存在且未过期则返回内容，否则返回None"""
    _ensure_cache_dir()
    key = _get_cache_key(exercise_name, user_profile)
    filepath = os.path.join(CACHE_DIR, f"{key}.json")
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 检查过期时间
        expires_at = datetime.fromisoformat(data['expires_at'])
        if datetime.now() > expires_at:
            # 缓存过期，删除文件
            os.remove(filepath)
            return None
        return data['content']
    except (json.JSONDecodeError, KeyError, IOError):
        # 文件损坏，删除
        try:
            os.remove(filepath)
        except:
            pass
        return None

def _make_json_serializable(obj):
    """递归地将对象转换为JSON可序列化的格式，处理Decimal等类型"""
    import decimal
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_serializable(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(_make_json_serializable(v) for v in obj)
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # 对于其他类型，尝试转换为字符串
        return str(obj)

def set_cached_description(exercise_name, user_profile, content, ttl_days=CACHE_TTL_DAYS):
    """将运动介绍存入缓存"""
    _ensure_cache_dir()
    key = _get_cache_key(exercise_name, user_profile)
    filepath = os.path.join(CACHE_DIR, f"{key}.json")
    expires_at = datetime.now() + timedelta(days=ttl_days)
    # 确保user_profile可序列化
    serializable_profile = _make_json_serializable(user_profile)
    data = {
        'exercise_name': exercise_name,
        'user_profile': serializable_profile,
        'content': content,
        'created_at': datetime.now().isoformat(),
        'expires_at': expires_at.isoformat()
    }
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False

def clear_expired_cache():
    """清理过期的缓存文件（可选，可以在后台任务中调用）"""
    _ensure_cache_dir()
    now = datetime.now()
    for filename in os.listdir(CACHE_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(CACHE_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                expires_at = datetime.fromisoformat(data['expires_at'])
                if now > expires_at:
                    os.remove(filepath)
            except:
                # 如果文件损坏，也删除
                try:
                    os.remove(filepath)
                except:
                    pass