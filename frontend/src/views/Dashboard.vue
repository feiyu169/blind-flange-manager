<template>
  <div class="dashboard">
    <h2>仪表盘</h2>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>待审批流程</span>
          </template>
          <div class="stat-value">{{ overview.pending_workflows || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>进行中流程</span>
          </template>
          <div class="stat-value">{{ overview.in_progress_workflows || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>异常盲板</span>
          </template>
          <div class="stat-value">{{ overview.abnormal_blind_flanges || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>库存预警</span>
          </template>
          <div class="stat-value">{{ overview.low_stock_alerts || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>盲板状态分布</span>
          </template>
          <div class="status-list">
            <div class="status-item">
              <span>在库</span>
              <span class="status-count">{{ overview.blind_flange_status_counts?.in_stock || 0 }}</span>
            </div>
            <div class="status-item">
              <span>已安装</span>
              <span class="status-count">{{ overview.blind_flange_status_counts?.installed || 0 }}</span>
            </div>
            <div class="status-item">
              <span>维护中</span>
              <span class="status-count">{{ overview.blind_flange_status_counts?.maintenance || 0 }}</span>
            </div>
            <div class="status-item">
              <span>已报废</span>
              <span class="status-count">{{ overview.blind_flange_status_counts?.scrapped || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近操作</span>
          </template>
          <el-table :data="activities" style="width: 100%">
            <el-table-column prop="action" label="操作" width="100" />
            <el-table-column prop="workflow_type" label="类型" width="100" />
            <el-table-column prop="notes" label="备注" />
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ new Date(row.created_at).toLocaleString() }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const overview = ref({})
const activities = ref([])

onMounted(async () => {
  await fetchOverview()
  await fetchActivities()
})

async function fetchOverview() {
  try {
    const response = await api.get('/api/v1/dashboard/overview')
    overview.value = response.data
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  }
}

async function fetchActivities() {
  try {
    const response = await api.get('/api/v1/dashboard/recent-activities')
    activities.value = response.data.items
  } catch (error) {
    console.error('获取最近操作失败:', error)
  }
}
</script>

<style scoped>
.dashboard h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #303133;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
  padding: 10px 0;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.status-count {
  font-weight: bold;
  color: #409eff;
}
</style>
