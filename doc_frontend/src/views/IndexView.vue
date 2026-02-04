<template>
  <div class="landing-container">
    <!-- 1. 顶部导航栏 -->
    <header class="navbar">
      <div class="logo">
        <el-icon class="logo-icon"><Cloudy /></el-icon>
        <span>凌云文档管理系统</span>
      </div>
      <div class="nav-buttons">
        <el-button @click="$router.push('/login')">登录</el-button>
        <el-button type="primary" @click="$router.push('/register')">注册账号</el-button>
      </div>
    </header>

    <!-- 2. Hero 区域 (Banner) -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">构建您的企业级<br>知识资产库</h1>
        <p class="hero-subtitle">
          安全存储、Markdown 在线协作、团队权限管理。<br>
          凌云系统，助您轻松驾驭海量技术文档。
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" class="start-btn" @click="$router.push('/register')">
            立即开始使用
            <el-icon class="el-icon--right"><Right /></el-icon>
          </el-button>
          <el-button size="large" round @click="$router.push('/login')">进入控制台</el-button>
        </div>
      </div>
      <div class="hero-image">
        <!-- 这里可以用 CSS 画一个示意图，或者放一张 SVG -->
        <div class="placeholder-img">
          <el-icon :size="100" color="#409EFF"><Document /></el-icon>
        </div>
      </div>
    </section>

    <!-- 3. 核心特性 -->
    <section class="features-section">
      <h2 class="section-title">核心功能</h2>
      <el-row :gutter="40" justify="center">
        <el-col :span="6">
          <el-card shadow="hover" class="feature-card">
            <el-icon :size="40" color="#409EFF"><Files /></el-icon>
            <h3>文档管理</h3>
            <p>支持 Markdown 在线编辑、实时预览、历史版本回溯与安全存储。</p>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="feature-card">
            <el-icon :size="40" color="#67C23A"><UserFilled /></el-icon>
            <h3>团队协作</h3>
            <p>精细化的 RBAC 权限控制，支持项目成员邀请、移除与角色管理。</p>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="feature-card">
            <el-icon :size="40" color="#E6A23C"><ChatLineSquare /></el-icon>
            <h3>问题追踪</h3>
            <p>内置 Issue 反馈系统，支持评论互动，让文档维护更高效。</p>
          </el-card>
        </el-col>
      </el-row>
    </section>

    <!-- 4. 底部 Footer -->
    <footer class="footer">
      <p>&copy; 2026 凌云文档管理系统. All Rights Reserved.</p>
    </footer>
  </div>
</template>

<script setup>
import { Cloudy, Right, Document, Files, UserFilled, ChatLineSquare } from '@element-plus/icons-vue'
</script>

<style scoped>
.landing-container {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  background-color: #fff;
}

/* 导航栏 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 50px;
  height: 64px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  z-index: 100;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.logo-icon {
  margin-right: 10px;
  color: #409EFF;
  font-size: 24px;
}

/* Hero 区域 */
.hero-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 80px 10%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 500px;
}

.hero-title {
  font-size: 48px;
  line-height: 1.2;
  color: #303133;
  margin-bottom: 20px;
}

.hero-subtitle {
  font-size: 18px;
  color: #606266;
  margin-bottom: 40px;
  line-height: 1.6;
}

.placeholder-img {
  width: 400px;
  height: 300px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 特性区域 */
.features-section {
  padding: 80px 10%;
  background: #fff;
}

.section-title {
  text-align: center;
  font-size: 32px;
  margin-bottom: 50px;
  color: #303133;
}

.feature-card {
  text-align: center;
  border: none;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-10px);
}

.feature-card h3 {
  margin: 20px 0 10px;
  font-size: 18px;
}

.feature-card p {
  color: #909399;
  font-size: 14px;
  line-height: 1.5;
}

/* Footer */
.footer {
  text-align: center;
  padding: 20px;
  background: #303133;
  color: #909399;
  font-size: 14px;
}
</style>