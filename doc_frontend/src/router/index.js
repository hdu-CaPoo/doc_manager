import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../views/Layout.vue'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import IndexView from '../views/IndexView.vue' // 1. 引入展示页组件

// 引入功能组件
const EditDoc = () => import('../views/project/EditDoc.vue')
const ProjectDetail = () => import('../views/project/ProjectDetail.vue')
const IssueDetail = () => import('../views/project/IssueDetail.vue') // 2. 引入问题详情组件
const RegisterView = () => import('../views/RegisterView.vue')
const ResetPwdView = () => import('../views/ResetPwdView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 3. 根路径指向展示页
    {
      path: '/',
      name: 'index',
      component: IndexView
    },
    
    // 4. 后台管理系统路径改为 /app
    {
      path: '/app',
      component: Layout,
      children: [
        // /app -> 显示项目列表
        { path: '', name: 'home', component: HomeView },
        
        // /app/profile -> 个人中心
        { path: 'profile', name: 'profile', component: () => import('../views/ProfileView.vue') },
        
        // /app/project/:id -> 项目详情
        { 
          path: 'project/:id', 
          name: 'project', 
          component: ProjectDetail,
          meta: { title: '项目详情' }
        },
        
        // /app/project/:id/doc/:docId -> 文档编辑
        {
          path: 'project/:id/doc/:docId',
          name: 'edit-doc',
          component: EditDoc,
          meta: { title: '编辑文档' }
        },
        
        // 5. 补充问题详情路由
        // /app/project/:id/issue/:issueId -> 问题详情
        {
          path: 'project/:id/issue/:issueId',
          name: 'issue-detail',
          component: IssueDetail,
          meta: { title: '问题详情' }
        }
      ]
    },
    
    // 登录注册相关页面（保持在根路径下）
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/reset-password', name: 'reset-password', component: ResetPwdView }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  // 白名单：不需要登录即可访问的页面
  const whiteList = ['index', 'login', 'register', 'reset-password']
  
  if (!whiteList.includes(to.name) && !token) {
    // 如果去的不是白名单页面且没有 token，跳转到登录页
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router