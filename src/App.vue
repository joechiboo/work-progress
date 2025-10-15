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
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">開始日期</label>
            <input
              type="date"
              v-model="filterStart"
              @change="applyFilter"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">結束日期</label>
            <input
              type="date"
              v-model="filterEnd"
              @change="applyFilter"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
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

        <!-- 智能彙總報告 -->
        <div v-for="project in analyzedProjects" :key="project.name" class="bg-white rounded-lg shadow p-6">
          <h3 class="text-2xl font-bold mb-4">
            🎯 {{ project.name}} 專案成果（{{ project.totalCommits }} commits）
          </h3>

          <!-- 功能分組 -->
          <div v-for="(feature, idx) in project.features" :key="idx" class="mb-6">
            <h4 class="text-lg font-bold mb-3">
              {{ idx + 1 }}. {{ feature.name }} {{ feature.icon }}
              <span class="text-sm text-gray-500 font-normal">({{ feature.dateRange }})</span>
            </h4>
            <p class="text-sm text-gray-600 mb-3">{{ feature.totalCommits }} 次提交</p>

            <!-- 子分組 -->
            <div v-for="(subgroup, subIdx) in feature.subgroups" :key="subIdx" class="ml-4 mb-4">
              <h5 class="font-semibold text-gray-800 mb-2">
                {{ subgroup.name }}
                <span class="text-xs text-gray-500">({{ subgroup.dateRange }})</span>
              </h5>
              <ul class="list-disc list-inside text-sm text-gray-700 space-y-1">
                <li v-for="(item, itemIdx) in subgroup.items" :key="itemIdx">
                  {{ item }}
                </li>
                <li v-if="subgroup.moreCount > 0" class="text-gray-500">
                  ... 以及其他 {{ subgroup.moreCount }} 項改進
                </li>
              </ul>
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
import { groupCommitsByFeature, cleanCommitMessage } from './utils/analyzer.js'

const rawData = ref(null)
const workData = ref(null)
const filterStart = ref('')
const filterEnd = ref('')

// 載入資料
onMounted(async () => {
  try {
    const response = await fetch(import.meta.env.BASE_URL + 'data/work-log-2025-07-15-to-2025-10-14.json')
    const data = await response.json()
    rawData.value = data
    workData.value = data

    // 設定預設篩選範圍：10/9 開始到今天
    const today = dayjs()
    const startDate = dayjs('2025-10-09')

    filterStart.value = startDate.format('YYYY-MM-DD')
    filterEnd.value = today.format('YYYY-MM-DD')

    // 自動套用兩週篩選
    applyFilter()
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

// 智能分析專案
const analyzedProjects = computed(() => {
  if (!workData.value) return []

  return workData.value.projects.map(project => {
    if (!project.commits || project.commits.length === 0) return null

    const { grouped, ungrouped } = groupCommitsByFeature(project.commits)

    const features = Object.values(grouped).map(feature => {
      const allCommits = [
        ...feature.commits,
        ...Object.values(feature.subgroups).flat()
      ]

      if (allCommits.length === 0) return null

      // 計算日期範圍
      const dates = allCommits.map(c => c.date).sort()
      const dateRange = dates.length > 1
        ? `${dates[0]} 至 ${dates[dates.length - 1]}`
        : dates[0]

      // 處理子分組
      const subgroups = Object.entries(feature.subgroups)
        .filter(([_, commits]) => commits.length > 0)
        .map(([name, commits]) => {
          const subDates = commits.map(c => c.date).sort()
          const subDateRange = subDates.length > 1
            ? `${subDates[0]} 至 ${subDates[subDates.length - 1]}`
            : subDates[0]

          const MAX_ITEMS = 5
          const items = commits.slice(0, MAX_ITEMS).map(c => cleanCommitMessage(c.message))
          const moreCount = Math.max(0, commits.length - MAX_ITEMS)

          return {
            name,
            dateRange: subDateRange,
            items,
            moreCount
          }
        })

      return {
        name: feature.name,
        icon: feature.icon,
        totalCommits: allCommits.length,
        dateRange,
        subgroups
      }
    }).filter(Boolean)

    return {
      name: project.name,
      totalCommits: project.totalCommits,
      features
    }
  }).filter(Boolean)
})
</script>
