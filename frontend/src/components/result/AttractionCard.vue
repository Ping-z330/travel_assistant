<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Attraction } from '../../types/trip'

const props = defineProps<{
  attraction: Attraction
}>()

const imageFailed = ref(false)
const isPreviewOpen = ref(false)
const shouldShowImage = computed(() => Boolean(props.attraction.image_url) && !imageFailed.value)

watch(
  () => props.attraction.image_url,
  () => {
    imageFailed.value = false
    isPreviewOpen.value = false
  },
)
</script>

<template>
  <article class="attraction-card">
    <button
      class="attraction-image"
      type="button"
      :disabled="!shouldShowImage"
      :aria-label="`查看${attraction.name}图片`"
      @click="isPreviewOpen = true"
    >
      <img
        v-if="shouldShowImage"
        :src="attraction.image_url"
        :alt="attraction.name"
        @error="imageFailed = true"
      />
      <em v-if="shouldShowImage">点击查看</em>
      <span v-else>{{ attraction.name.slice(0, 1) }}</span>
    </button>

    <div class="attraction-body">
      <div class="attraction-title-row">
        <h4>{{ attraction.name }}</h4>
        <span v-if="attraction.category" class="attraction-category">
          {{ attraction.category }}
        </span>
      </div>
      <div class="attraction-meta">
        <span>{{ attraction.visit_duration }} 分钟</span>
        <span>¥{{ attraction.ticket_price }}</span>
      </div>
      <p class="attraction-address">{{ attraction.address }}</p>
      <p class="attraction-reason">{{ attraction.description }}</p>
    </div>
  </article>

  <Teleport to="body">
    <div
      v-if="isPreviewOpen && shouldShowImage"
      class="image-preview"
      role="dialog"
      aria-modal="true"
      :aria-label="`${attraction.name}图片预览`"
      @click.self="isPreviewOpen = false"
    >
      <button class="preview-close" type="button" aria-label="关闭图片预览" @click="isPreviewOpen = false">
        ×
      </button>
      <figure class="preview-figure">
        <img :src="attraction.image_url" :alt="attraction.name" />
        <figcaption>{{ attraction.name }}</figcaption>
      </figure>
    </div>
  </Teleport>
</template>

<style scoped>
.attraction-card {
  display: grid;
  grid-template-columns: minmax(300px, 38%) minmax(0, 1fr);
  overflow: hidden;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.attraction-image {
  position: relative;
  display: grid;
  width: 100%;
  min-height: 220px;
  padding: 0;
  place-items: center;
  overflow: hidden;
  color: #ffffff;
  border: 0;
  background:
    linear-gradient(rgba(23, 107, 93, 0.42), rgba(23, 107, 93, 0.74)),
    linear-gradient(135deg, #176b5d, #d88b2d);
  cursor: zoom-in;
}

.attraction-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.25s ease;
}

.attraction-image:hover img {
  transform: scale(1.04);
}

.attraction-image:disabled {
  cursor: default;
}

.attraction-image em {
  position: absolute;
  right: 12px;
  bottom: 12px;
  padding: 6px 10px;
  color: #ffffff;
  background: rgba(15, 49, 42, 0.76);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  backdrop-filter: blur(8px);
  font-size: 12px;
  font-style: normal;
  font-weight: 900;
}

.attraction-image span {
  font-size: 44px;
  font-weight: 900;
}

.attraction-body {
  display: grid;
  gap: 9px;
  align-content: start;
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
  line-height: 1.35;
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
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.attraction-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 9px;
  color: var(--primary-dark);
  background: var(--soft);
  border: 1px solid rgba(23, 107, 93, 0.1);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.attraction-address {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: var(--primary-dark);
  font-size: 13px;
  font-weight: 700;
  line-height: 1.55;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.attraction-reason {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.image-preview {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 32px;
  background: rgba(8, 19, 17, 0.82);
}

.preview-close {
  position: fixed;
  top: 22px;
  right: 24px;
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  font-size: 28px;
  line-height: 1;
}

.preview-figure {
  display: grid;
  gap: 12px;
  max-width: min(1060px, 92vw);
  max-height: 88vh;
  margin: 0;
}

.preview-figure img {
  max-width: 100%;
  max-height: 82vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.36);
}

.preview-figure figcaption {
  color: rgba(255, 255, 255, 0.86);
  font-size: 15px;
  font-weight: 800;
  text-align: center;
}

@media (max-width: 720px) {
  .attraction-card {
    grid-template-columns: 1fr;
  }

  .attraction-image {
    min-height: auto;
    aspect-ratio: 16 / 10;
  }
}
</style>
