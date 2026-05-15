<template>
  <div class="workflow-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>流程列表</span>
          <el-button type="primary" @click="handleCreate">新建流程</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="类型">
          <el-select v-model="searchForm.type" placeholder="全部" clearable>
            <el-option label="安装" value="install" />
            <el-option label="拆卸" value="uninstall" />
            <el-option label="巡检" value="inspect" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="待审批" value="pending" />
            <el-option label="已审批" value="approved" />
            <el-option label="已驳回" value="rejected" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="blind_flange_id" label="盲板ID" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" />
        <el-table-column prop="applied_at" label="申请时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.applied_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="success" link @click="handleApprove(row)"
            >审批</el-button>
            <el-button
              v-if="row.status === 'approved'"
              type="warning" link @click="handleStart(row)"
            >开始</el-button>
            <el-button
              v-if="row.status === 'in_progress'"
              type="success" link @click="handleComplete(row)"
            >完成</el-button>
            <el-button
              v-if="['pending', 'approved', 'in_progress'].includes(row.status)"
              type="danger" link @click="handleCancel(row)"
            >取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新建流程对话框 -->
    <el-dialog v-model="dialogVisible" title="新建流程" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="流程类型" prop="type">
          <el-select v-model="form.type">
            <el-option label="安装" value="install" />
            <el-option label="拆卸" value="uninstall" />
            <el-option label="巡检" value="inspect" />
          </el-select>
        </el-form-item>
        <el-form-item label="盲板ID" prop="blind_flange_id">
          <el-input-number v-model="form.blind_flange_id" :min="1" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  type: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const form = reactive({
  type: 'install',
  blind_flange_id: 1,
  notes: '',
})

const rules = {
  type: [{ required: true, message: '请选择流程类型', trigger: 'change' }],
  blind_flange_id: [{ required: true, message: '请输入盲板ID', trigger: 'blur' }],
}

onMounted(() => {
  fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
    }
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })

    const response = await api.get('/api/v1/workflows', { params })
    tableData.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  searchForm.type = ''
  searchForm.status = ''
  handleSearch()
}

function handleSizeChange() {
  pagination.page = 1
  fetchData()
}

function handleCurrentChange() {
  fetchData()
}

function handleCreate() {
  dialogVisible.value = true
}

function handleView(row) {
  ElMessage.info(`查看流程 ${row.id}`)
}

async function handleApprove(row) {
  try {
    await ElMessageBox.confirm('确定审批通过该流程吗？', '提示', { type: 'info' })
    await api.put(`/api/v1/workflows/${row.id}/approve`, { approved: true, notes: '审批通过' })
    ElMessage.success('审批成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('审批失败')
    }
  }
}

async function handleStart(row) {
  try {
    await api.put(`/api/v1/workflows/${row.id}/start`)
    ElMessage.success('已开始执行')
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleComplete(row) {
  try {
    await api.put(`/api/v1/workflows/${row.id}/complete`)
    ElMessage.success('已完成')
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm('确定取消该流程吗？', '提示', { type: 'warning' })
    await api.put(`/api/v1/workflows/${row.id}/cancel`, { reason: '用户取消' })
    ElMessage.success('已取消')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    await api.post('/api/v1/workflows', form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    submitLoading.value = false
  }
}

function getTypeTag(type) {
  const map = { install: 'success', uninstall: 'danger', inspect: 'warning' }
  return map[type] || 'info'
}

function getTypeLabel(type) {
  const map = { install: '安装', uninstall: '拆卸', inspect: '巡检' }
  return map[type] || type
}

function getStatusTag(status) {
  const map = {
    pending: 'info', approved: 'success', rejected: 'danger',
    in_progress: 'warning', completed: 'success', cancelled: 'info'
  }
  return map[status] || 'info'
}

function getStatusLabel(status) {
  const map = {
    pending: '待审批', approved: '已审批', rejected: '已驳回',
    in_progress: '进行中', completed: '已完成', cancelled: '已取消'
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

.search-form {
  margin-bottom: 20px;
}
</style>
