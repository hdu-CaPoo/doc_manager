<template>
  <el-table :data="docs" style="width: 100%" v-loading="loading">
    <el-table-column prop="original_filename" label="文件名" />
    <el-table-column label="操作">
      <template #default="scope">
         <el-button link type="success" @click="restore(scope.row)">恢复</el-button>
         <!-- 新增：彻底删除按钮 -->
         <el-button link type="danger" @click="hardDelete(scope.row)">彻底删除</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus' // 引入 ElMessageBox

const props = defineProps(['projectId'])
const docs = ref([])
const loading = ref(false) // 添加 loading 状态

const fetchTrash = async () => {
  loading.value = true
  try {
    docs.value = await request.get(`/projects/${props.projectId}/trashbin`)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const restore = async (row) => {
   try {
     await request.get(`/projects/${props.projectId}/docs/${row.id}/restore`)
     ElMessage.success('已恢复')
     fetchTrash()
   } catch (e) {
     console.error(e)
   }
}

// 新增：彻底删除逻辑
const hardDelete = (row) => {
  ElMessageBox.confirm(
    '此操作将永久删除该文件，无法恢复。是否继续?',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      // 调用后端硬删除接口 [1]
      await request.delete(`/projects/${props.projectId}/docs/${row.id}/hard_delete`)
      ElMessage.success('彻底删除成功')
      fetchTrash() // 刷新列表
    } catch (e) {
      console.error(e)
    }
  }).catch(() => {
    // 取消操作
  })
}

onMounted(fetchTrash)
</script>