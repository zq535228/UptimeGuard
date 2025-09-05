# 通知去重功能说明

## 功能概述

为了避免在网站监控过程中连续发送相同的失败或成功通知消息，我们实现了通知去重功能。该功能能够智能地判断何时应该发送通知，避免重复通知的困扰。

## 核心特性

### ✅ 避免重复通知
- **相同故障不重复通知**: 当网站连续失败次数相同时，不会重复发送故障通知
- **相同恢复不重复通知**: 当网站保持正常状态时，不会重复发送恢复通知

### ✅ 智能更新通知
- **故障次数增加**: 当连续失败次数增加时，会发送更新通知
- **状态切换**: 当网站从故障状态恢复到正常状态时，会发送恢复通知

### ✅ 阈值控制
- **未达阈值不通知**: 只有当连续失败次数达到设定阈值时，才会发送故障通知
- **可配置阈值**: 支持通过配置文件或环境变量设置失败阈值

## 实现原理

### 1. 通知状态跟踪
系统为每个监控的网站维护一个通知状态记录，包含：
- `status`: 最后通知的状态（"down" 或 "up"）
- `timestamp`: 最后通知时间
- `consecutive_failures`: 最后通知时的连续失败次数

### 2. 去重逻辑
```python
# 故障通知去重逻辑
def should_send_down_notification(url, current_status, consecutive_failures, failure_threshold):
    # 1. 当前状态必须是故障
    if current_status != "down":
        return False
    
    # 2. 连续失败次数必须达到阈值
    if consecutive_failures < failure_threshold:
        return False
    
    # 3. 检查历史通知状态
    last_state = get_last_notification_state(url)
    
    # 4. 如果没有历史状态，可以发送通知
    if last_state is None:
        return True
    
    # 5. 如果最后通知的是相同故障，不重复发送
    if (last_state.get("status") == "down" and 
        last_state.get("consecutive_failures") == consecutive_failures):
        return False
    
    # 6. 如果故障次数增加，可以发送更新通知
    if (last_state.get("status") == "down" and 
        consecutive_failures > last_state.get("consecutive_failures", 0)):
        return True
    
    # 7. 如果从正常状态变成故障，可以发送通知
    if last_state.get("status") == "up":
        return True
    
    return False
```

### 3. 状态管理
- **状态更新**: 每次发送通知后，系统会更新对应网站的通知状态
- **状态清理**: 当网站被删除时，会自动清理对应的通知状态
- **状态持久化**: 通知状态会保存到 `notification_state.json` 文件中

## 使用方法

### 1. 自动使用
通知去重功能已经集成到监控系统中，无需额外配置即可使用。

### 2. 手动管理
通过 Web 界面可以：
- 查看当前所有网站的通知状态
- 清除所有通知状态（重置去重逻辑）
- 配置失败阈值

### 3. 编程接口
```python
from notification_tracker import (
    should_send_down_notification,
    should_send_recovery_notification,
    update_notification_state,
    clear_site_state
)

# 检查是否应该发送故障通知
should_notify = should_send_down_notification(
    site_url="https://example.com",
    current_status="down",
    consecutive_failures=5,
    failure_threshold=3
)

# 更新通知状态
if should_notify:
    update_notification_state("https://example.com", "down", 5)
```

## 配置选项

### 环境变量
- `TELEGRAM_FAILURE_THRESHOLD`: 连续失败阈值（默认: 10）

### 配置文件
在 `telegram_config.json` 中设置：
```json
{
  "failure_threshold": 10
}
```

## 测试验证

### 运行测试
```bash
python3 test_notification_deduplication.py
```

### 运行演示
```bash
python3 demo_notification_deduplication.py
```

## 文件结构

```
UptimeGuard/
├── notification_tracker.py          # 通知状态跟踪模块
├── test_notification_deduplication.py  # 测试脚本
├── demo_notification_deduplication.py  # 演示脚本
├── notification_state.json          # 通知状态存储文件
└── NOTIFICATION_DEDUPLICATION.md    # 本文档
```

## 注意事项

1. **状态文件**: `notification_state.json` 文件会在首次使用时自动创建
2. **状态清理**: 建议定期清理过期的通知状态，避免文件过大
3. **并发安全**: 当前实现适用于单进程环境，多进程环境可能需要额外考虑
4. **错误处理**: 如果状态文件损坏，系统会自动重新初始化

## 故障排除

### 问题1: 通知状态文件损坏
**症状**: 程序启动时报错或通知逻辑异常
**解决**: 删除 `notification_state.json` 文件，系统会自动重新创建

### 问题2: 通知去重不生效
**症状**: 仍然收到重复通知
**解决**: 
1. 检查 `notification_state.json` 文件是否存在且可写
2. 查看日志中的通知状态更新记录
3. 尝试清除所有通知状态重新开始

### 问题3: 状态不同步
**症状**: 通知状态与实际监控状态不一致
**解决**: 使用 Web 界面的"清除所有通知状态"功能重置状态

## 更新日志

- **v1.0.0**: 初始版本，实现基本的通知去重功能
- 支持故障通知去重
- 支持恢复通知去重
- 支持故障次数更新通知
- 支持状态切换通知
- 支持阈值控制
- 支持状态管理界面
