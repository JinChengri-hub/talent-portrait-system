<template>
  <div class="app-header">
    <div class="header-left">
      <el-icon class="menu-icon"><Expand /></el-icon>
      <span class="welcome-text">欢迎回来，管理员</span>
    </div>
    <div class="header-right">
      <el-badge :value="5" class="notify-badge">
        <el-button link class="header-btn">
          <el-icon><Bell /></el-icon>
          通知
        </el-button>
      </el-badge>
      <el-button link class="header-btn logout-btn">
        <el-icon><SwitchButton /></el-icon>
        退出
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.app-header {
  height: 56px;
  min-height: 56px;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-icon {
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
}

.welcome-text {
  font-size: 14px;
  color: var(--text-secondary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-btn {
  color: var(--text-secondary) !important;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.header-btn:hover {
  color: var(--accent-cyan) !important;
}

.logout-btn:hover {
  color: var(--accent-red) !important;
}

.notify-badge :deep(.el-badge__content) {
  background-color: var(--accent-red);
}
</style>
