<script setup>
import { computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  EditOutlined,
  DatabaseOutlined,
  ShareAltOutlined,
  LineChartOutlined,
  TableOutlined,
  DashboardOutlined,
  CloudServerOutlined,
  SettingOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const user = useUserStore()

const selectedKeys = computed(() => [route.name])

const menuItems = [
  { key: 'editor', icon: () => h(EditOutlined), label: '创作工作台' },
  { key: 'knowledge', icon: () => h(DatabaseOutlined), label: '知识库' },
  { key: 'graph', icon: () => h(ShareAltOutlined), label: '知识图谱' },
  { key: 'style', icon: () => h(LineChartOutlined), label: '风格报告' },
  { key: 'matrix', icon: () => h(TableOutlined), label: '内容矩阵' },
  { key: 'dashboard', icon: () => h(DashboardOutlined), label: '数据看板' },
  { key: 'llm', icon: () => h(CloudServerOutlined), label: 'LLM 监控' },
  { key: 'settings', icon: () => h(SettingOutlined), label: '设置' },
]

function onMenuClick({ key }) {
  router.push({ name: key })
}

const toggleSidebar = () => {
  user.sidebarCollapsed = !user.sidebarCollapsed
}

const handleLogout = () => {
  console.log('logout')
}

// 动态计算宽度和间距
const sidebarWidth = computed(() => user.sidebarCollapsed ? '80px' : '260px')
</script>

<template>
  <a-layout class="app-layout">
    <!-- 固定侧边栏 -->
    <a-layout-sider
      v-model:collapsed="user.sidebarCollapsed"
      class="app-layout__sider"
      :width="260"
      :collapsed-width="80"
      :trigger="null"
      collapsible
    >
      <div class="app-layout__brand" @click="toggleSidebar">
        <div class="app-layout__logo-main">
          <div class="app-layout__logo-inner" />
        </div>
        <div v-if="!user.sidebarCollapsed" class="app-layout__brand-text">
          <span class="app-layout__title">Creator Copilot</span>
          <span class="app-layout__subtitle">AI CO-CREATOR</span>
        </div>
      </div>

      <a-menu
        mode="inline"
        :selected-keys="selectedKeys"
        :items="menuItems"
        class="app-layout__menu"
        @click="onMenuClick"
      />

      <div class="app-layout__sider-footer">
        <div class="app-layout__collapse-btn" @click="toggleSidebar">
          <MenuUnfoldOutlined v-if="user.sidebarCollapsed" />
          <MenuFoldOutlined v-else />
        </div>
      </div>
    </a-layout-sider>

    <!-- 主容器 -->
    <a-layout class="app-layout__main">
      <a-layout-header class="app-layout__header">
        <div class="app-layout__header-container">
          <div class="app-layout__header-left">
            <div class="app-layout__page-info">
              <span class="app-layout__page-tag">PAGE</span>
              <h2 class="app-layout__page-title">{{ menuItems.find(m => m.key === route.name)?.label }}</h2>
            </div>
          </div>

          <div class="app-layout__header-actions">
            <div class="app-layout__icon-btn">
              <a-badge dot :offset="[-2, 2]">
                <BellOutlined />
              </a-badge>
            </div>

            <a-dropdown placement="bottomRight" :trigger="['click']">
              <div class="app-layout__user-trigger">
                <div class="app-layout__user-info">
                  <span class="app-layout__user-name">{{ user.displayName }}</span>
                  <span class="app-layout__user-role">创作者</span>
                </div>
                <a-avatar :size="40" class="app-layout__avatar">
                  <template #icon><UserOutlined /></template>
                </a-avatar>
              </div>
              <template #overlay>
                <a-menu class="app-layout__user-dropdown">
                  <a-menu-item key="profile"><UserOutlined /> 个人资料</a-menu-item>
                  <a-menu-item key="settings"><SettingOutlined /> 账号设置</a-menu-item>
                  <a-menu-divider />
                  <a-menu-item key="logout" @click="handleLogout" danger>
                    <LogoutOutlined /> 退出登录
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </div>
      </a-layout-header>

      <a-layout-content class="app-layout__content">
        <div class="app-layout__inner">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<style scoped lang="scss">
@use '@/assets/styles/variables' as *;

.app-layout {
  min-height: 100vh;
  background: $color-bg-muted;
  overflow: hidden;
}

// 侧边栏固定
.app-layout__sider {
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  background: #ffffff !important;
  z-index: 1001;
  border-right: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 1px 0 10px rgba(0, 0, 0, 0.02);
}

.app-layout__brand {
  height: 80px;
  display: flex;
  align-items: center;
  padding: 0 22px;
  cursor: pointer;
  border-bottom: 1px solid rgba(0, 0, 0, 0.02);
}

.app-layout__logo-main {
  width: 36px;
  height: 36px;
  background: $color-black;
  border-radius: 10px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.app-layout__logo-inner {
  width: 14px;
  height: 14px;
  border: 2px solid #ffffff;
  border-radius: 4px;
  transform: rotate(45deg);
}

.app-layout__brand-text {
  margin-left: 14px;
  display: flex;
  flex-direction: column;
  white-space: nowrap;
}

.app-layout__title {
  font-family: $font-display;
  font-size: 1.2rem;
  font-weight: 500;
  color: $color-black;
  line-height: 1.1;
}

.app-layout__subtitle {
  font-size: 0.6rem;
  letter-spacing: 0.25em;
  color: $color-text-muted;
  text-transform: uppercase;
}

.app-layout__menu {
  padding: 16px 12px;
  background: transparent !important;
  border: none !important;

  :deep(.ant-menu-item) {
    height: 48px;
    margin-bottom: 4px;
    border-radius: 12px;
    &.ant-menu-item-selected {
      background: $color-warm-stone !important;
      color: $color-black !important;
      font-weight: 600;
    }
  }
}

.app-layout__sider-footer {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  padding: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.03);
}

.app-layout__collapse-btn {
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px; cursor: pointer; color: $color-text-muted;
  &:hover { background: $color-bg-muted; color: $color-black; }
}

// 主区域
.app-layout__main {
  padding-left: v-bind(sidebarWidth); // 使用 padding 代替 margin，确保内部元素宽度计算正确
  transition: padding-left 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  background: $color-bg-muted;
  min-height: 100vh;
  width: 100%; // 关键：容器宽度
}

.app-layout__header {
  height: 80px;
  line-height: 80px;
  padding: 0;
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 1000;
  width: 100%;
}

.app-layout__header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px; // 在这里定义内边距，防止溢出
  height: 100%;
  width: 100%;
}

.app-layout__page-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  line-height: 1.2;
}

.app-layout__page-tag {
  font-size: 10px;
  letter-spacing: 0.1em;
  color: $color-text-muted;
  font-weight: 700;
}

.app-layout__page-title {
  font-family: $font-display;
  font-weight: 300;
  font-size: 1.6rem;
  color: $color-black;
  margin: 0;
}

.app-layout__header-actions {
  display: flex;
  align-items: center;
  gap: 24px;
}

.app-layout__icon-btn {
  font-size: 20px;
  color: $color-text-secondary;
  cursor: pointer;
  display: flex; align-items: center;
  &:hover { color: $color-black; }
}

.app-layout__user-trigger {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 4px 4px 4px 16px;
  border-radius: 99px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.3s ease;
  &:hover {
    background: #ffffff;
    border-color: rgba(0, 0, 0, 0.06);
    box-shadow: $shadow-soft;
  }
}

.app-layout__user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.2;
}

.app-layout__user-name {
  font-size: 14px;
  font-weight: 600;
  color: $color-black;
}

.app-layout__user-role {
  font-size: 11px;
  color: $color-text-muted;
}

.app-layout__avatar {
  background: $color-black !important;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.app-layout__content {
  padding: 48px 40px;
}

.app-layout__inner {
  max-width: 1200px;
  margin: 0 auto;
}

.app-layout__user-dropdown {
  min-width: 160px;
  padding: 8px;
  :deep(.ant-menu-item) { border-radius: 8px; }
}
</style>
