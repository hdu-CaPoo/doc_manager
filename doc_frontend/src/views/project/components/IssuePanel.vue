<template>
  <div>
    <!-- 顶部工具栏 -->
    <div class="mb-3">
      <el-button type="primary" @click="dialogVisible = true">提出问题</el-button>
    </div>

    <!-- 问题列表表格 -->
    <el-table :data="issues" style="width: 100%" v-loading="loading">
      <el-table-column prop="title" label="标题" />
      
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <!-- 状态标签：open 为红色，其他为绿色 -->
          <el-tag :type="scope.row.status === 'open' ? 'danger' : 'success'">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="priority" label="优先级" width="100">
         <template #default="scope">
           <el-tag effect="plain" :type="getPriorityType(scope.row.priority)">
             {{ scope.row.priority }}
           </el-tag>
         </template>
      </el-table-column>
      
      <el-table-column prop="created_at" label="提问时间" width="180">
        <template #default="scope">{{ new Date(scope.row.created_at).toLocaleDateString() }}</template>
      </el-table-column>
      
      <el-table-column label="操作" width="150">
         <template #default="scope">
            <!-- 绑定点击事件，跳转到详情页 -->
            <el-button link type="primary" @click="goDetail(scope.row)">查看详情</el-button>
         </template>
      </el-table-column>
    </el-table>

    <!-- 提问弹窗 -->
    <el-dialog v-model="dialogVisible" title="提出新问题" width="40%">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="简短描述问题" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority" placeholder="请选择">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input 
            v-model="form.content" 
            type="textarea" 
            rows="4" 
            placeholder="详细描述你的问题..." 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createIssue">提交</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router' // 记得导入 useRouter

const props = defineProps(['projectId'])
const router = useRouter() // 获取路由实例

const issues = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({ title: '', content: '', priority: 'medium' })

// 1. 获取问题列表
const fetchIssues = async () => {
  loading.value = true
  try {
    // API: GET /projects/{id}/issues [1]
    issues.value = await request.get(`/projects/${props.projectId}/issues`)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// 2. 提交新问题
const createIssue = async () => {
  if (!form.title || !form.content) return ElMessage.warning('标题和内容不能为空')

  try {
    // API: POST /projects/{id}/issue/create [1]
    // 注意：后端定义这个接口接收的是 application/x-www-form-urlencoded
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('content', form.content)
    formData.append('priority', form.priority)
    
    await request.post(`/projects/${props.projectId}/issue/create`, formData)
    
    ElMessage.success('提交成功')
    dialogVisible.value = false
    // 清空表单
    form.title = ''
    form.content = ''
    form.priority = 'medium'
    
    // 刷新列表
    fetchIssues()
  } catch (e) {
    console.error(e)
  }
}

// 3. 跳转详情页
const goDetail = (row) => {
  router.push({
    name: 'issue-detail', // 对应路由里配置的 name
    params: { 
      id: props.projectId, // 对应路由里的 :id
      issueId: row.id      // 对应路由里的 :issueId
    }
  })
}

// 辅助函数：根据优先级返回标签颜色
const getPriorityType = (p) => {
    if (p === 'high') return 'danger'
    if (p === 'medium') return 'warning'
    return 'info'
}

onMounted(fetchIssues)
</script>

<style scoped>
.mb-3 { margin-bottom: 15px; }
</style>