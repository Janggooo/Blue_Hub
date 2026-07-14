<script setup>
import { ref, onMounted } from 'vue'
import client from '../api/client'
import OrgCard from '../components/OrgCard.vue'
import SearchFilterBar from '../components/SearchFilterBar.vue'

const orgs = ref([])
const categories = ref([])
const filters = ref({ q: '', category: '' })
const loading = ref(true)
const error = ref('')

async function fetchOrgs() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/organizations', { params: filters.value })
    orgs.value = data
  } catch (e) {
    error.value = 'Could not load organizations right now.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await client.get('/categories')
    categories.value = data
  } catch (e) { /* non-critical */ }
  fetchOrgs()
})
</script>

<template>
  <div class="container">
    <div class="page-head">
      <h1>Organization Directory</h1>
      <p class="subtitle">Find a student organization that matches your interests.</p>
    </div>

    <SearchFilterBar v-model="filters" :categories="categories" @search="fetchOrgs" />

    <div v-if="error" class="error-banner">{{ error }}</div>
    <div v-else-if="loading" class="empty-state">Loading organizations…</div>
    <div v-else-if="orgs.length === 0" class="empty-state">No organizations match your search.</div>
    <div v-else class="grid">
      <OrgCard v-for="o in orgs" :key="o.organization_id" :org="o" />
    </div>
  </div>
</template>

<style scoped>
.page-head { margin-bottom: 24px; }
.subtitle { color: var(--ink-soft); margin-top: 6px; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}
</style>
