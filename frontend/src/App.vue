<script setup>
import zhCN from 'ant-design-vue/es/locale/zh_CN'

const theme = {
  token: {
    colorPrimary: '#000000',
    colorBgLayout: '#f5f5f5',
    colorBgContainer: '#ffffff',
    colorText: '#4e4e4e',
    colorTextHeading: '#000000',
    colorBorder: '#e5e5e5',
    colorBorderSecondary: 'rgba(0, 0, 0, 0.05)',
    borderRadius: 12,
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
    fontSize: 16,
    controlHeight: 40,
  },
  components: {
    Button: {
      borderRadius: 9999,
      controlHeight: 40,
      fontWeight: 500,
      paddingInline: 24,
      boxShadow: 'none',
    },
    Layout: {
      headerBg: '#ffffff',
      bodyBg: '#f5f5f5',
      siderBg: '#ffffff',
    },
    Menu: {
      itemBorderRadius: 10,
      fontSize: 15,
      itemSelectedBg: '#f5f2ef',
      itemSelectedColor: '#000000',
    },
    Card: {
      borderRadiusLG: 20,
      boxShadowTertiary: 'rgba(0, 0, 0, 0.06) 0 0 0 1px, rgba(0, 0, 0, 0.04) 0 1px 2px, rgba(0, 0, 0, 0.04) 0 2px 4px',
    },
    Input: {
      borderRadius: 12,
      controlHeight: 44,
    },
    Select: {
      borderRadius: 12,
      controlHeight: 44,
    },
  },
}
</script>

<template>
  <a-config-provider :locale="zhCN" :theme="theme">
    <router-view />
  </a-config-provider>
</template>
