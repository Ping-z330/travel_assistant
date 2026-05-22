<script setup lang="ts">
import type { Attraction } from '../../types/trip'

defineProps<{
  attraction: Attraction
}>()
</script>

<template>
  <article class="attraction-card">
    <div class="attraction-image">
      <img v-if="attraction.image_url" :src="attraction.image_url" :alt="attraction.name" />
      <span v-else>{{ attraction.name.slice(0, 1) }}</span>
    </div>

    <div class="attraction-body">
      <div class="attraction-title-row">
        <h4>{{ attraction.name }}</h4>
        <span v-if="attraction.category" class="attraction-category">
          {{ attraction.category }}
        </span>
      </div>
      <p class="attraction-meta">
        {{ attraction.visit_duration }} 分钟 / {{ attraction.ticket_price }} 元
      </p>
      <p class="attraction-reason">{{ attraction.description }}</p>
    </div>
  </article>
</template>

<style scoped>
.attraction-card {
  overflow: hidden;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.attraction-image {
  display: grid;
  aspect-ratio: 16 / 10;
  place-items: center;
  overflow: hidden;
  color: #ffffff;
  background:
    linear-gradient(rgba(23, 107, 93, 0.42), rgba(23, 107, 93, 0.74)),
    linear-gradient(135deg, #176b5d, #d88b2d);
}

.attraction-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.attraction-image span {
  font-size: 44px;
  font-weight: 900;
}

.attraction-body {
  display: grid;
  gap: 8px;
  padding: 16px;
}

.attraction-title-row {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
}

.attraction-card h4 {
  margin: 0;
  color: var(--text);
  font-size: 18px;
}

.attraction-category {
  flex: 0 0 auto;
  padding: 4px 8px;
  color: var(--primary-dark);
  background: var(--soft);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.attraction-meta {
  margin: 0;
  color: var(--primary-dark);
  font-size: 14px;
  font-weight: 800;
}

.attraction-reason {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}
</style>
