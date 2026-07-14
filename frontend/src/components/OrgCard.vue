<script setup>
defineProps({ org: { type: Object, required: true } })
</script>

<template>
  <RouterLink :to="`/organizations/${org.organization_id}`" class="org-card">
    <h3>{{ org.organization_name }}</h3>
    <span v-if="org.category" class="tag">{{ org.category }}</span>
    <p class="desc">{{ org.description }}</p>
  </RouterLink>
</template>

<style scoped>
.org-card {
  display: block;
  background: var(--paper-raised);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 20px;
  color: var(--ink);
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.org-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(18, 35, 61, 0.08);
}
h3 { font-size: 1.1rem; margin-bottom: 8px; }
.desc {
  color: var(--ink-soft);
  font-size: 0.9rem;
  margin-top: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
