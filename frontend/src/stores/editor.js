import { defineStore } from 'pinia'

export const useEditorStore = defineStore('editor', {
  state: () => ({
    taskId: null,
    topic: '',
    imageSource: 'random',
    status: 'idle',
    currentNode: '',
    titles: [],
    outline: null,
    contentMd: '',
    history: [],
    interruptKind: null,
    lastError: null,
  }),
  actions: {
    reset() {
      this.taskId = null
      this.topic = ''
      this.status = 'idle'
      this.currentNode = ''
      this.titles = []
      this.outline = null
      this.contentMd = ''
      this.history = []
      this.interruptKind = null
      this.lastError = null
    },
    applyStreamPayload(acc) {
      if (acc.task_id) this.taskId = acc.task_id
      if (acc.topic) this.topic = acc.topic
      if (acc.current_node) this.currentNode = acc.current_node
      if (acc.titles) this.titles = acc.titles
      if (acc.outline) this.outline = acc.outline
      if (acc.content) this.contentMd = acc.content
      if (acc.history) this.history = acc.history
    },
  },
})
