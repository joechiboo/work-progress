<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-gray-900">📊 工作進度追蹤系統</h1>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-8">
      <!-- 時間篩選 -->
      <div v-if="rawData" class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">🔍 時間區間篩選</h2>
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <label class="block text-sm font-medium text-gray-700 mb-1">開始日期</label>
            <input
              type="date"
              v-model="filterStart"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div class="flex-1">
            <label class="block text-sm font-medium text-gray-700 mb-1">結束日期</label>
            <input
              type="date"
              v-model="filterEnd"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            @click="applyFilter"
            class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            套用篩選
          </button>
          <button
            @click="resetFilter"
            class="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
          >
            重置
          </button>
        </div>
      </div>

      <!-- 資料總覽 -->
      <div v-if="workData" class="space-y-6">
        <!-- 期間與作者 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-2xl font-bold mb-4">
            📈 您的工作成果（{{ workData.author }}）
          </h2>
          <p class="text-gray-600">{{ displayPeriod.start }} 至 {{ displayPeriod.end }}</p>
          <p class="text-sm text-gray-500 mt-1">
            共 {{ displayPeriod.days }} 天 ({{ displayPeriod.weeks }} 週)
          </p>
        </div>

        <!-- 統計卡片 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-gray-600 mb-2">總提交次數</div>
            <div class="text-3xl font-bold text-blue-600">{{ displaySummary.totalCommits }}</div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-gray-600 mb-2">專案數量</div>
            <div class="text-3xl font-bold text-green-600">{{ displaySummary.projectCount }}</div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="text-gray-600 mb-2">日均提交</div>
            <div class="text-3xl font-bold text-purple-600">{{ displaySummary.dailyAverage }}</div>
          </div>
        </div>

        <!-- 專案列表 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-xl font-bold mb-4">🎯 專案成果</h3>
          <div class="space-y-4">
            <div
              v-for="project in displayProjects"
              :key="project.name"
              class="border-l-4 border-blue-500 pl-4 py-2"
            >
              <div class="flex justify-between items-start">
                <div>
                  <h4 class="font-bold text-lg">{{ project.name }}</h4>
                  <p class="text-gray-600">{{ project.totalCommits }} 次提交</p>
                </div>
                <span class="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                  {{ project.percentage }}%
                </span>
              </div>

              <!-- Commits 列表 -->
              <div v-if="project.commits && project.commits.length" class="mt-4">
                <details class="cursor-pointer">
                  <summary class="text-sm font-medium text-gray-700 hover:text-blue-600">
                    查看 {{ project.commits.length }} 個 commits
                  </summary>
                  <div class="mt-3 space-y-2 max-h-96 overflow-y-auto">
                    <div
                      v-for="(commit, idx) in project.commits"
                      :key="commit.hash"
                      class="p-3 bg-gray-50 rounded text-sm border-l-2"
                      :class="getCategoryColor(commit.category)"
                    >
                      <div class="flex justify-between items-start mb-1">
                        <span class="font-mono text-xs text-gray-500">{{ commit.hash.substring(0, 7) }}</span>
                        <span class="text-xs text-gray-600">{{ commit.date }}</span>
                      </div>
                      <div class="font-medium text-gray-800">{{ commit.message }}</div>
                      <div v-if="commit.category" class="mt-1">
                        <span class="text-xs px-2 py-1 rounded-full bg-gray-200 text-gray-700">
                          {{ commit.category }}
                        </span>
                      </div>
                    </div>
                  </div>
                </details>
              </div>
            </div>
          </div>
        </div>

        <!-- 分類統計 -->
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-xl font-bold mb-4">📊 分類統計</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              v-for="(count, category) in categoryStats"
              :key="category"
              class="p-4 rounded-lg border-2"
              :class="getCategoryColor(category)"
            >
              <div class="text-sm text-gray-600">{{ category }}</div>
              <div class="text-2xl font-bold">{{ count }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 載入中或無資料 -->
      <div v-else class="text-center py-12">
        <p class="text-gray-500">載入資料中...</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'

const rawData = ref(null)
const workData = ref(null)
const filterStart = ref('')
const filterEnd = ref('')

// 載入資料
onMounted(async () => {
  try {
    const response = await fetch('/data/work-log-2024-09-17-to-10-08.json')
    const data = await response.json()
    rawData.value = data
    workData.value = data

    // 設定預設篩選範圍
    if (data.period.start && data.period.end) {
      filterStart.value = data.period.start
      filterEnd.value = data.period.end
    }
  } catch (error) {
    console.error('載入資料失敗：', error)
  }
})

// 套用篩選
const applyFilter = () => {
  if (!rawData.value) return

  const start = filterStart.value ? dayjs(filterStart.value) : null
  const end = filterEnd.value ? dayjs(filterEnd.value) : null

  const filteredProjects = rawData.value.projects.map(project => {
    if (!project.commits) return project

    const filteredCommits = project.commits.filter(commit => {
      const commitDate = dayjs(commit.date)
      if (start && commitDate.isBefore(start)) return false
      if (end && commitDate.isAfter(end)) return false
      return true
    })

    return {
      ...project,
      commits: filteredCommits,
      totalCommits: filteredCommits.length
    }
  }).filter(p => p.totalCommits > 0)

  workData.value = {
    ...rawData.value,
    projects: filteredProjects
  }
}

// 重置篩選
const resetFilter = () => {
  workData.value = rawData.value
  if (rawData.value.period.start && rawData.value.period.end) {
    filterStart.value = rawData.value.period.start
    filterEnd.value = rawData.value.period.end
  }
}

// 顯示期間
const displayPeriod = computed(() => {
  if (!workData.value) return { start: '', end: '', days: 0, weeks: 0 }

  const start = filterStart.value || workData.value.period.start
  const end = filterEnd.value || workData.value.period.end

  const startDay = dayjs(start)
  const endDay = dayjs(end)
  const days = endDay.diff(startDay, 'day') + 1
  const weeks = Math.ceil(days / 7)

  return { start, end, days, weeks }
})

// 顯示統計
const displaySummary = computed(() => {
  if (!workData.value) return { totalCommits: 0, projectCount: 0, dailyAverage: 0 }

  const totalCommits = workData.value.projects.reduce((sum, p) => sum + p.totalCommits, 0)
  const projectCount = workData.value.projects.filter(p => p.totalCommits > 0).length

  const days = displayPeriod.value.days || 1
  const dailyAverage = (totalCommits / days).toFixed(1)

  return { totalCommits, projectCount, dailyAverage }
})

// 顯示專案（計算百分比）
const displayProjects = computed(() => {
  if (!workData.value) return []

  const total = displaySummary.value.totalCommits
  return workData.value.projects.map(p => ({
    ...p,
    percentage: total > 0 ? Math.round((p.totalCommits / total) * 100) : 0
  }))
})

// 分類統計
const categoryStats = computed(() => {
  if (!workData.value) return {}

  const stats = {}
  workData.value.projects.forEach(project => {
    if (!project.commits) return
    project.commits.forEach(commit => {
      const cat = commit.category || '未分類'
      stats[cat] = (stats[cat] || 0) + 1
    })
  })

  return stats
})

// 分類顏色
const getCategoryColor = (category) => {
  const colors = {
    '功能開發': 'border-blue-300 bg-blue-50',
    '錯誤修正': 'border-red-300 bg-red-50',
    '重構': 'border-purple-300 bg-purple-50',
    '效能優化': 'border-green-300 bg-green-50',
    '文檔': 'border-yellow-300 bg-yellow-50',
    '測試': 'border-pink-300 bg-pink-50',
    '樣式': 'border-indigo-300 bg-indigo-50',
    '配置': 'border-gray-300 bg-gray-50',
    '部署': 'border-orange-300 bg-orange-50',
    '其他': 'border-gray-300 bg-gray-50',
    '未分類': 'border-gray-200 bg-gray-50'
  }
  return colors[category] || colors['未分類']
}
</script>
