<template>
  <div class="inventory-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>库存管理</span>
          <el-button type="primary" @click="handleIn">入库</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="编码/名称"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 库存汇总表格 -->
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="blind_flange_code" label="盲板编码" width="120" />
        <el-table-column prop="blind_flange_name" label="盲板名称" width="150" />
        <el-table-column prop="current_stock" label="当前库存" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.is_alert }">{{ row.current_stock }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="alert_threshold" label="预警阈值" width="120">
          <template #default="{ row }">
            {{ row.alert_threshold || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_alert" label="预警状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_alert ? 'danger' : 'success'">
              {{ row.is_alert ? '库存不足' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleInItem(row)">入库</el-button>
            <el-button type="warning" link @click="handleOutItem(row)">出库</el-button>
            <el-button type="info" link @click="handleRecords(row)">记录</el-button>
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

    <!-- 入库/出库对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="盲板ID" prop="blind_flange_id">
          <el-input-number v-model="form.blind_flange_id" :min="1" :disabled="!!currentItem" />
        </el-form-item>
        <el-form-item label="操作类型" prop="type">
          <el-select v-model="form.type">
            <el-option label="入库" value="in" />
            <el-option label="出库" value="out" />
            <el-option label="调整" value="adjust" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="form.reason" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 库存记录对话框 -->
    <el-dialog v-model="recordsVisible" title="库存记录" width="800px">
      <el-table :data="records" style="width: 100%">
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100" />
        <el-table-column prop="reason" label="原因" />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const recordsVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref(null)
const currentItem = ref(null)
const records = ref([])

const searchForm = reactive({
  keyword: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const form = reactive({
  blind_flange_id: 1,
  type: 'in',
  quantity: 1,
  reason: '',
})

const rules = {
  blind_flange_id: [{ required: true, message: '请输入盲板ID', trigger: 'blur' }],
  type: [{ required: true, message: '请选择操作类型', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
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

    const response = await api.get('/api/v1/inventory/summary', { params })
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
  searchForm.keyword = ''
  handleSearch()
}

function handleSizeChange() {
  pagination.page = 1
  fetchData()
}

function handleCurrentChange() {
  fetchData()
}

function handleIn() {
  dialogTitle.value = '入库'
  currentItem.value = null
  form.blind_flange_id = 1
  form.type = 'in'
  form.quantity = 1
  form.reason = ''
  dialogVisible.value = true
}

function handleInItem(row) {
  dialogTitle.value = '入库'
  currentItem.value = row
  form.blind_flange_id = row.blind_flange_id
  form.type = 'in'
  form.quantity = 1
  form.reason = ''
  dialogVisible.value = true
}

function handleOutItem(row) {
  dialogTitle.value = '出库'
  currentItem.value = row
  form.blind_flange_id = row.blind_flange_id
  form.type = 'out'
  form.quantity = 1
  form.reason = ''
  dialogVisible.value = true
}

async function handleRecords(row) {
  try {
    const response = await api.get('/api/v1/inventory', {
      params: { blind_flange_id: row.blind_flange_id }
    })
    records.value = response.data.items
    recordsVisible.value = true
  } catch (error) {
    ElMessage.error('获取记录失败')
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    await api.post('/api/v1/inventory', form)
    ElMessage.success('操作成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

function getTypeTag(type) {
  const map = { in: 'success', out: 'danger', adjust: 'warning' }
  return map[type] || 'info'
}

function getTypeLabel(type) {
  const map = { in: '入库', out: '出库', adjust: '调整' }
  return map[type] || type
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

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}
</style>
