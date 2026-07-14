<script setup>
defineProps({
  modelValue: { type: Object, required: true },
  categories: { type: Array, default: () => [] },
  showDateFilters: { type: Boolean, default: false }
})
defineEmits(['update:modelValue', 'search'])
</script>

<template>
  <div class="search-bar card">
    <input
      class="q"
      type="search"
      placeholder="Search…"
      :value="modelValue.q"
      @input="$emit('update:modelValue', { ...modelValue, q: $event.target.value })"
      @keyup.enter="$emit('search')"
    />
    <select
      :value="modelValue.category"
      @change="$emit('update:modelValue', { ...modelValue, category: $event.target.value })"
    >
      <option value="">All categories</option>
      <option v-for="c in categories" :key="c.category_id" :value="c.category_name">{{ c.category_name }}</option>
    </select>

    <template v-if="showDateFilters">
      <div class="date-filter">
        <label for="date_from">Event date</label>
        <input
          id="date_from"
          type="date"
          :value="modelValue.date_from"
          @change="$emit('update:modelValue', { ...modelValue, date_from: $event.target.value })"
        />
      </div>
    </template>

    <button class="btn btn-primary" @click="$emit('search')">Search</button>
  </div>
</template>

<style scoped>
.search-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 28px;
}
.q { flex: 2; min-width: 200px; }
select, input[type="date"] { flex: 1; min-width: 140px; }
.date-filter {
  display: flex;
  flex-direction: column;
  min-width: 170px;
}
.date-filter label {
  font-size: 0.85rem;
  color: var(--ink-soft);
  margin-bottom: 4px;
}
input, select {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px 12px;
  background: #fff;
  color: var(--ink);
}
</style>
