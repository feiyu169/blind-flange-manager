<template>
  <div class="inspection-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>巡检管理</span>
          <el-button type="primary" @click="handleCreate">新建巡检计划</el-button>
        </div>
      </template>

      <!-- 标签页 -->
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="巡检计划" name="plans">
          <!-- 巡检计划表格 -->
          <el-table :data="plans" style="width: 100%" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="blind_flange_id" label="盲板ID" width="100" />
            <el-table-column prop="cycle_days" label="巡检周期(天)" width="120" />
            <el-table-column prop="next_inspected_at" label="下次巡检" width="180">
              <template #default="{ row }">
                {{ row.next_inspected_at ? new Date(row.next_inspected_at).toLocaleDateString() : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'">
                  {{ row.is_active ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="待巡检" name="due">
          <!-- 待巡检表格 -->
          <el-table :data="dueList" style="width: 100%" v-loading="loading">
            <el-table-column prop="blind_flange_code" label="盲板编码" width="120" />
            <el-table-column prop="blind_flange_name" label="盲板名称" width="150" />
            <el-table-column prop="cycle_days" label="周期(天)" width="100" />
            <el-table-column prop="next_inspected_at" label="计划时间" width="180">
              <template #default="{ row }">
                {{ row.next_inspected_at ? new Date(row.next_inspected_at).toLocaleDateString() : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="is_overdue" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.is_overdue ? 'danger' : 'success'">
                  {{ row.is_overdue ? '已逾期' : '正常' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleRecord(row)">巡检</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="巡检记录" name="records">
          <!-- 巡检记录表格 -->
          <el-table :data="records" style="width: 100%" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="blind_flange_id" label="盲板ID" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'normal' ? 'success' : 'danger'">
                  {{ row.status === 'normal' ? '正常' : '异常' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" />
            <el-table-column prop="inspected_at" label="巡检时间" width="180">
              <template #default="{ row }">
                {{ new Date(row.inspected_at).toLocaleString() }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 新建/编辑巡检计划对话框 -->
    <el-dialog v-model="planDialogVisible" :title="planDialogTitle" width="500px">
      <el-form ref="planFormRef" :model="planForm" :rules="planRules" label-width="100px">
        <el-form-item label="盲板ID" prop="blind_flange_id">
          <el-input-number v-model="planForm.blind_flange_id" :min="1" />
        </el-form-item>
        <el-form-item label="巡检周期" prop="cycle_days">
          <el-input-number v-model="planForm.cycle_days" :min="1" :max="365" />
          <span style="margin-left: 10px">天</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePlanSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 巡检记录对话框 -->
    <el-dialog v-model="recordDialogVisible" title="巡检记录" width="500px">
      <el-form ref="recordFormRef" :model="recordForm" :rules="recordRules" label-width="100px">
        <el-form-item label="盲板ID">
          <el-input :value="recordForm.blind_flange_id" disabled />
        </el-form-item>
        <el-form-item label="巡检状态" prop="status">
          <el-radio-group v-model="recordForm.status">
            <el-radio label="normal">正常</el-radio>
            <el-radio label="abnormal">异常</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="recordForm.notes" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="recordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRecordSubmit" :loading="submitLoading">确定</el-button>
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
const activeTab = ref('plans')
const plans = ref([])
const dueList = ref([])
const records = ref([])

const planDialogVisible = ref(false)
const planDialogTitle = ref('')
const planFormRef = ref(null)
const currentPlanId = ref(null)

const recordDialogVisible = ref(false)
const recordFormRef = ref(null)

const planForm = reactive({
  blind_flange_id: 1,
  cycle_days: 30,
})

const recordForm = reactive({
  blind_flange_id: null,
  inspection_plan_id: null,
  status: 'normal',
  notes: '',
})

const planRules = {
  blind_flange_id: [{ required: true, message: '请输入盲板ID', trigger: 'blur' }],
  cycle_days: [{ required: true, message: '请输入巡检周期', trigger: 'blur' }],
}

const recordRules = {
  status: [{ required: true, message: '请选择巡检状态', trigger: 'change' }],
}

onMounted(() => {
  fetchPlans()
})

function handleTabClick(tab) {
  if (tab.name === 'plans') {
    fetchPlans()
  } else if (tab.name === 'due') {
    fetchDueList()
  } else if (tab.name === 'records') {
    fetchRecords()
  }
}

async function fetchPlans() {
  loading.value = true
  try {
    const response = await api.get('/api/v1/inspections/plans')
    plans.value = response.data.items
  } catch (error) {
    ElMessage.error('获取巡检计划失败')
  } finally {
    loading.value = false
  }
}

async function fetchDueList() {
  loading.value = true
  try {
    const response = await api.get('/api/v1/inspections/plans/due/list')
    dueList.value = response.data.items
  } catch (error) {
    ElMessage.error('获取待巡检列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchRecords() {
  loading.value = true
  try {
    const response = await api.get('/api/v1/inspections/records')
    records.value = response.data.items
  } catch (error) {
    ElMessage.error('获取巡检记录失败')
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  planDialogTitle.value = '新建巡检计划'
  currentPlanId.value = null
  planForm.blind_flange_id = 1
  planForm.cycle_days = 30
  planDialogVisible.value = true
}

function handleEdit(row) {
  planDialogTitle.value = '编辑巡检计划'
  currentPlanId.value = row.id
  planForm.blind_flange_id = row.blind_flange_id
  planForm.cycle_days = row.cycle_days
  planDialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定删除该巡检计划吗？', '提示', { type: 'warning' })
    await api.delete(`/api/v1/inspections/plans/${row.id}`)
    ElMessage.success('删除成功')
    fetchPlans()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleRecord(row) {
  recordForm.blind_flange_id = row.blind_flange_id
  recordForm.inspection_plan_id = row.plan_id
  recordForm.status = 'normal'
  recordForm.notes = ''
  recordDialogVisible.value = true
}

async function handlePlanSubmit() {
  const valid = await planFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    if (currentPlanId.value) {
      await api.put(`/api/v1/inspections/plans/${currentPlanId.value}`, planForm)
      ElMessage.success('更新成功')
    } else {
      await api.post('/api/v1/inspections/plans', planForm)
      ElMessage.success('创建成功')
    }
    planDialogVisible.value = false
    fetchPlans()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

async function handleRecordSubmit() {
  const valid = await recordFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    await api.post('/api/v1/inspections/records', recordForm)
    ElMessage.success('巡检记录已提交')
    recordDialogVisible.value = false
    fetchDueList()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '提交失败')
  } finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
