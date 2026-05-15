<template>
  <div class="blind-flange-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>盲板详情</span>
          <el-button @click="router.push('/blind-flanges')">返回列表</el-button>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="编码">{{ blindFlange.code }}</el-descriptions-item>
        <el-descriptions-item label="名称">{{ blindFlange.name }}</el-descriptions-item>
        <el-descriptions-item label="规格型号">{{ blindFlange.specification || '-' }}</el-descriptions-item>
        <el-descriptions-item label="材质">{{ blindFlange.material || '-' }}</el-descriptions-item>
        <el-descriptions-item label="压力等级">{{ blindFlange.pressure_rating || '-' }}</el-descriptions-item>
        <el-descriptions-item label="尺寸">{{ blindFlange.size || '-' }}</el-descriptions-item>
        <el-descriptions-item label="安装位置">{{ blindFlange.location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="管道编号">{{ blindFlange.pipeline_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="法兰编号">{{ blindFlange.flange_no || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(blindFlange.status)">
            {{ getStatusLabel(blindFlange.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ blindFlange.notes || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ new Date(blindFlange.created_at).toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ new Date(blindFlange.updated_at).toLocaleString() }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 状态变更日志 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <span>状态变更日志</span>
      </template>
      <el-table :data="statusLogs" style="width: 100%">
        <el-table-column prop="old_status" label="原状态" width="120">
          <template #default="{ row }">
            {{ getStatusLabel(row.old_status) || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="new_status" label="新状态" width="120">
          <template #default="{ row }">
            {{ getStatusLabel(row.new_status) }}
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../../api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const blindFlange = ref({})
const statusLogs = ref([])

onMounted(() => {
  fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const id = route.params.id
    const [detailRes, logsRes] = await Promise.all([
      api.get(`/api/v1/blind-flanges/${id}`),
      api.get(`/api/v1/blind-flanges/${id}/status-logs`),
    ])
    blindFlange.value = detailRes.data
    statusLogs.value = logsRes.data
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

function getStatusType(status) {
  const map = {
    in_stock: 'success',
    installed: 'primary',
    maintenance: 'warning',
    scrapped: 'danger',
  }
  return map[status] || 'info'
}

function getStatusLabel(status) {
  const map = {
    in_stock: '在库',
    installed: '已安装',
    maintenance: '维护中',
    scrapped: '已报废',
  }
  return map[status] || status
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
