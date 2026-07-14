<script setup>
import { ref, onMounted } from 'vue'
import client from '../api/client'
import EventCard from '../components/EventCard.vue'
import SearchFilterBar from '../components/SearchFilterBar.vue'

const events = ref([])
const categories = ref([])
const filters = ref({ q: '', category: '', date_from: '', date_to: '' })
const loading = ref(true)
const error = ref('')

async function fetchEvents() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get('/events', { params: filters.value })
    events.value = data
  } catch (e) {
    error.value = 'Could not load events right now.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await client.get('/categories')
    categories.value = data
  } catch (e) {
    // categories are optional; ignore failures
  }
  fetchEvents()
})
</script>

<template>
  <div class="container">
    <div class="page-head">
      <div>
        <h1>Event Directory</h1>
        <p class="subtitle">Everything happening across ADNU organizations, in one place.</p>
      </div>
    </div>

    <SearchFilterBar v-model="filters" :categories="categories" show-date-filters @search="fetchEvents" />

    <div v-if="error" class="error-banner">{{ error }}</div>
    <div v-else-if="loading" class="empty-state">Loading events…</div>
    <div v-else-if="events.length === 0" class="empty-state">
      No events match your search. Try a different keyword or filter.
    </div>
    <div v-else class="grid">
      <EventCard v-for="e in events" :key="e.event_id" :event="e" />
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
