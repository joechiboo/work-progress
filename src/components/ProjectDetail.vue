<template>
  <div class="space-y-6">
    <!-- 明細資料載入中 -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-500">載入 commit 明細中…</p>
      <p class="text-xs text-gray-400 mt-2">明細檔約 1.5 MB，只在開啟這個分頁時下載一次</p>
    </div>

    <div v-else-if="error" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-red-600">明細載入失敗：{{ error }}</p>
    </div>

    <template v-else>
      <!-- 專案選單 -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-center mb-3">
          <h3 class="text-xl font-bold">📝 專案明細</h3>
          <span class="text-sm text-gray-500">
            {{ analyzedProjects.length }} 個專案 ·
            {{ analyzedProjects.reduce((s, p) => s + p.totalCommits, 0) }} commits
          </span>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="p in analyzedProjects"
            :key="p.name"
            @click="selected = p.name"
            :class="[
              'px-3 py-1.5 text-sm rounded-lg transition-colors',
              selected === p.name
                ? 'bg-blue-600 text-white font-semibold'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            {{ p.name }}
            <span :class="selected === p.name ? 'text-blue-100' : 'text-gray-500'">
              {{ p.totalCommits }}
            </span>
          </button>
        </div>
      </div>

      <div v-if="!analyzedProjects.length" class="bg-white rounded-lg shadow p-12 text-center text-gray-400">
        這個區間沒有資料
      </div>

      <!-- 單一專案的彙總報告 -->
      <div v-if="currentProject" class="bg-white rounded-lg shadow p-6">
        <h3 class="text-2xl font-bold mb-4">
          🎯 {{ currentProject.name }} 專案成果（{{ currentProject.totalCommits }} commits）
        </h3>

        <div v-for="(feature, idx) in currentProject.features" :key="idx" class="mb-6">
          <h4 class="text-lg font-bold mb-3">
            {{ idx + 1 }}. {{ feature.name }} {{ feature.icon }}
            <span class="text-sm text-gray-500 font-normal">({{ feature.dateRange }})</span>
          </h4>
          <p class="text-sm text-gray-600 mb-3">{{ feature.totalCommits }} 次提交</p>

          <div v-for="(subgroup, subIdx) in feature.subgroups" :key="subIdx" class="ml-4 mb-4">
            <h5 class="font-semibold text-gray-800 mb-2">
              {{ subgroup.name }}
              <span class="text-xs text-gray-500">({{ subgroup.dateRange }})</span>
            </h5>
            <ul class="list-disc list-inside text-sm text-gray-700 space-y-1">
              <li v-for="(item, itemIdx) in subgroup.items" :key="itemIdx">
                {{ item }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { groupCommitsByFeature, cleanCommitMessage } from '../utils/analyzer.js'

const props = defineProps({
  // 已依日期／專案類型篩選過的 projects（含 commits）
  projects: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' }
})

const selected = ref(null)

const analyzedProjects = computed(() => {
  return props.projects.map(project => {
    if (!project.commits || project.commits.length === 0) return null

    const { grouped, ungrouped } = groupCommitsByFeature(project.commits)

    const features = Object.values(grouped).map(feature => {
      const allCommits = [
        ...feature.commits,
        ...Object.values(feature.subgroups).flat()
      ]
      if (allCommits.length === 0) return null

      const dates = allCommits.map(c => c.date).sort()
      const dateRange = dates.length > 1
        ? `${dates[0]} 至 ${dates[dates.length - 1]}`
        : dates[0]

      const subgroups = Object.entries(feature.subgroups)
        .filter(([, commits]) => commits.length > 0)
        .map(([name, commits]) => {
          const subDates = commits.map(c => c.date).sort()
          return {
            name,
            dateRange: subDates.length > 1
              ? `${subDates[0]} 至 ${subDates[subDates.length - 1]}`
              : subDates[0],
            items: commits.map(c => cleanCommitMessage(c.message))
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

    if (ungrouped.length > 0) {
      const dates = ungrouped.map(c => c.date).sort()
      const dateRange = dates.length > 1
        ? `${dates[0]} 至 ${dates[dates.length - 1]}`
        : dates[0]

      features.push({
        name: features.length > 0 ? '其他變更' : '所有變更',
        icon: '📝',
        totalCommits: ungrouped.length,
        dateRange,
        subgroups: [{
          name: '近期提交',
          dateRange,
          items: ungrouped.map(c => `[${c.date}] ${cleanCommitMessage(c.message)}`)
        }]
      })
    }

    return {
      name: project.name,
      totalCommits: project.totalCommits,
      features
    }
  }).filter(Boolean)
})

const currentProject = computed(() => {
  const list = analyzedProjects.value
  if (!list.length) return null
  return list.find(p => p.name === selected.value) || list[0]
})

// 篩選變動後若原本選的專案沒了，回到第一個
watch(analyzedProjects, list => {
  if (!list.some(p => p.name === selected.value)) {
    selected.value = list.length ? list[0].name : null
  }
})
</script>
