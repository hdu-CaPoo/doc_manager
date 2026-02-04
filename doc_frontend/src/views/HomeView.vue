<template>
  <div class="container">
    <div class="header">
      <h2>我的项目</h2>
      <!-- 这里的退出登录按钮可以保留，也可以去掉，因为 Layout 里有了 -->
    </div>
    
    <el-row :gutter="20">
      <el-col :span="6" v-for="p in projects" :key="p.id">
        <!-- 修改点 1：添加 @click 事件和 cursor: pointer 样式 -->
        <el-card 
          shadow="hover" 
          style="margin-bottom: 20px; cursor: pointer;" 
          @click="goProject(p.id)"
        >
          <h3>{{ p.name }}</h3>
          <p class="desc">{{ p.description || '暂无描述' }}</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { useRouter } from 'vue-router'

const projects = ref([])
const router = useRouter()

// 页面加载时获取数据
onMounted(async () => {
  try {
    const res = await request.get('/projects/')
    projects.value = res
  } catch (e) {
    console.error(e)
  }
})

// 修改点 2：添加跳转函数
const goProject = (id) => {
  // 跳转到我们之前定义的详情页路由 /project/:id
  router.push(`/app/project/${id}`)
}
</script>

<style scoped>
.container { padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
/* 增加一点描述文字的样式，防止太长 */
.desc { color: #666; font-size: 14px; margin-top: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>