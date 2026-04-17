import { defineStore } from 'pinia'

export const useStatsStore = defineStore('stats', {
  state: () => ({
    dashboard: null,
    loading: false,
  }),
  actions: {
    setDashboard(data) {
      this.dashboard = data
    },
  },
})
