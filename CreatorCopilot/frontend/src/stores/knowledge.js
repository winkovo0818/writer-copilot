import { defineStore } from 'pinia'

export const useKnowledgeStore = defineStore('knowledge', {
  state: () => ({
    articles: [],
    searchResults: [],
    loading: false,
  }),
  actions: {
    setArticles(list) {
      this.articles = list || []
    },
    setSearchResults(list) {
      this.searchResults = list || []
    },
  },
})
