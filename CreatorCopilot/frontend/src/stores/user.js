import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    displayName: '创作者',
    sidebarCollapsed: false,
  }),
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
  },
})
