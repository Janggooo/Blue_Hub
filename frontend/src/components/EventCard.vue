<script setup>
defineProps({ event: { type: Object, required: true } })

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<template>
  <RouterLink :to="`/events/${event.event_id}`" class="event-card">
    <div class="date-tab">{{ formatDate(event.event_date) }}</div>
    <h3>{{ event.title }}</h3>
    <p class="org">{{ event.organization_name }}</p>
    <p class="venue" v-if="event.venue">📍 {{ event.venue }}</p>
    <span v-if="event.category" class="tag">{{ event.category }}</span>
  </RouterLink>
</template>

<style scoped>
.event-card {
  display: block;
  background: var(--paper-raised);
  border: 1px solid var(--line);
  border-left: 4px solid var(--cobalt);
  border-radius: 10px;
  padding: 18px;
  color: var(--ink);
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(18, 35, 61, 0.08);
}
.date-tab {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--cobalt);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
}
h3 { font-size: 1.1rem; margin-bottom: 4px; }
.org { color: var(--ink-soft); font-size: 0.9rem; margin: 0 0 6px; }
.venue { color: var(--ink-soft); font-size: 0.85rem; margin: 0 0 10px; }
</style>
