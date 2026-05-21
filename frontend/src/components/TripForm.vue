<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { generateTripPlan } from '../services/tripApi'
import type { TripPlanRequest } from '../types/trip'

const preferences = ['自然风光', '历史人文', '美食探索', '亲子轻松', '紧凑打卡']

// form表单数据模型
const form = reactive({
  city: '',
  startDate: '',
  days: 3,
  budget: 3000,
  people: 2,
  preference: '自然风光',
})

// loading状态和错误信息、路由实例
const loading = ref(false)
const errorMessage = ref('')
const router = useRouter()

// 提交表单并生成旅行计划
const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const request: TripPlanRequest = {
      city: form.city,
      start_date: form.startDate,
      days: form.days,
      budget: form.budget,
      people: form.people,
      preference: form.preference,
    }
    // 发送请求并将结果存储在 sessionStorage 中，然后跳转到结果页
    const response = await generateTripPlan(request)
    // 将旅行计划数据存储在 sessionStorage 中，以便在结果页获取
    sessionStorage.setItem('tripPlan', JSON.stringify(response))
    router.push('/result')
  } catch (error) {
    errorMessage.value = '生成旅行计划时发生错误，请稍后重试。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="trip-page">
    <a class="brand-logo" href="/" aria-label="智能旅游助手首页">
      <span class="brand-en">AI-TRAVEL-ASSISTANT</span>
      <div class="brand-main">
        <span class="brand-mark">旅</span>
        <span class="brand-text">智能旅游助手</span>
      </div>
      <div class="brand-slogan">
        <span class="brand-slogan-line">旅途最迷人的地方</span>
        <span class="brand-slogan-line brand-slogan-muted">在于没人知道你从哪里来，又要去哪里......</span>
      </div>
    </a>

    <section class="form-panel" aria-labelledby="trip-form-title">
      <div class="form-heading">
        <p class="eyebrow">Step 1</p>
        <h2 id="trip-form-title">填写旅行信息</h2>
      </div>

      <form class="trip-form" @submit.prevent="handleSubmit">
        <label>
          <span>目的地城市</span>
          <input v-model.trim="form.city" type="text" placeholder="例如：北京" required />
        </label>

        <div class="form-grid">
          <label>
            <span>出发日期</span>
            <input v-model="form.startDate" type="date" required />
          </label>

          <label>
            <span>游玩天数</span>
            <input v-model.number="form.days" type="number" min="1" max="15" required />
          </label>
        </div>

        <div class="form-grid">
          <label>
            <span>总预算</span>
            <input v-model.number="form.budget" type="number" min="0" step="100" required />
          </label>

          <label>
            <span>出行人数</span>
            <input v-model.number="form.people" type="number" min="1" max="20" required />
          </label>
        </div>

        <label>
          <span>旅行偏好</span>
          <select v-model="form.preference">
            <option v-for="item in preferences" :key="item" :value="item">
              {{ item }}
            </option>
          </select>
        </label>

        <button class="submit-button" type="submit" :disabled="loading">
          {{ loading ? '生成中...' : '生成旅行计划' }}
        </button>

        <!-- 错误信息 -->
        <p v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </p>
      </form>
    </section>

    <footer class="site-footer">
      <span>© 2026 AI Travel Assistant. All rights reserved.</span>
    </footer>
  </main>
</template>

<style scoped>
.trip-page {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: 96px 20px 86px;
  background:
    linear-gradient(rgba(16, 67, 58, 0.72), rgba(16, 67, 58, 0.88)),
    url("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80");
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

.brand-logo {
  position: absolute;
  top: 28px;
  left: 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
  color: #ffffff;
  text-decoration: none;
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.3);
}

.brand-en {
  padding-left: 41px;
  font-size: 23px;
  font-weight: 800;
  letter-spacing: 0.4em;
  opacity: 0.8;
}

.brand-main {
  display: inline-flex;
  gap: 12px;
  align-items: center;
}

.brand-mark {
  display: inline-grid;
  width: 56px;
  height: 56px;
  place-items: center;
  color: #ebe47d;
  font-size: 30px;
  font-weight: 900;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 0 8px 30px rgba(0,0,0,0.2);
}

.brand-text {
  font-size: 60px;
  line-height: 1.05;
  font-weight: 800;
  letter-spacing: 2px;
  background: linear-gradient(90deg,#ffffff,#d6f5e8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-slogan {
  display: grid;
  margin-top: 20px;
  gap: 2px;
  max-width: 560px;
}

.brand-slogan-line {
  display: block;
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  line-height: 1.8;
  font-weight: 500;
  letter-spacing: 0.04em;
}

.brand-slogan-muted {
  color: rgba(255, 255, 255, 0.72);
  font-weight: 400;
}

.form-panel {
  width: min(100%, 520px);
  padding: 40px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 8px;
  box-shadow: 0 28px 80px rgba(8, 29, 26, 0.28);
  backdrop-filter: blur(16px);
}

.form-heading {
  margin-bottom: 28px;
}

.eyebrow {
  margin: 0 0 12px;
  color: var(--accent);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h2,
p {
  margin-top: 0;
}

h2 {
  margin-bottom: 0;
  font-size: 30px;
  line-height: 1.18;
}

.trip-form {
  display: grid;
  gap: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

label {
  display: grid;
  gap: 8px;
  color: var(--text);
  font-size: 15px;
  font-weight: 700;
}

input,
select {
  width: 100%;
  min-height: 48px;
  padding: 0 14px;
  color: var(--text);
  background: #fbfcfa;
  border: 1px solid var(--line);
  border-radius: 6px;
  outline: none;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease;
}

input:focus,
select:focus {
  background: #ffffff;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(23, 107, 93, 0.12);
}

.submit-button {
  width: 100%;
  min-height: 52px;
  margin-top: 8px;
  color: #ffffff;
  background: var(--primary);
  border: 0;
  border-radius: 6px;
  font-weight: 800;
  transition:
    background 0.2s ease,
    transform 0.2s ease;
}

.submit-button:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

.error-message {
  margin: 10px 0 0;
  color: #b42318;
  font-size: 14px;
  font-weight: 600;
}

.site-footer {
  position: absolute;
  right: 32px;
  bottom: 24px;
  left: 32px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.72);
  font-size: 13px;
  letter-spacing: 0.04em;
  text-align: center;
}

@media (max-width: 860px) {
  .trip-page {
    padding: 92px 14px 78px;
  }

  .form-panel {
    padding: 28px;
  }
}

@media (max-width: 560px) {
  .brand-logo {
    top: 20px;
    left: 20px;
  }

  .site-footer {
    right: 18px;
    bottom: 18px;
    left: 18px;
    gap: 6px 14px;
    font-size: 12px;
  }

  .brand-text {
    font-size: 24px;
  }

  .brand-mark {
    width: 44px;
    height: 44px;
    font-size: 23px;
  }

  .brand-en {
    font-size: 12px;
  }

  .brand-slogan {
    max-width: 300px;
  }

  .brand-slogan-line {
    font-size: 14px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-panel {
    padding: 24px;
  }

}
</style>
