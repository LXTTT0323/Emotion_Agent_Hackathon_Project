describe('Preference Page', () => {
  beforeEach(() => {
    // 访问偏好设置页面
    cy.visit('/');
  });

  it('displays the preference form', () => {
    // 检查表单标题
    cy.contains('设置您的偏好').should('be.visible');
    
    // 检查表单字段
    cy.contains('label', '用户名').should('be.visible');
    cy.contains('label', 'MBTI 性格类型').should('be.visible');
    cy.contains('label', '对话风格').should('be.visible');
    cy.contains('label', '年龄').should('be.visible');
    cy.contains('label', '星座').should('be.visible');
    
    // 检查提交按钮
    cy.contains('button', '保存并开始聊天').should('be.visible');
  });

  it('validates username field', () => {
    // 点击提交按钮而不填写用户名
    cy.contains('button', '保存并开始聊天').click();
    
    // 检查错误消息
    cy.contains('用户名不能为空').should('be.visible');
  });

  it('validates age field', () => {
    // 填写无效的年龄值
    cy.get('input[name="username"]').type('测试用户');
    cy.get('input[name="age"]').type('abc');
    
    // 点击提交按钮
    cy.contains('button', '保存并开始聊天').click();
    
    // 检查错误消息
    cy.contains('年龄必须是有效的数字').should('be.visible');
  });

  it('submits form successfully', () => {
    // 拦截API请求
    cy.intercept('POST', '/agent/preferences', {
      statusCode: 200,
      body: { success: true, message: '用户偏好设置已更新' }
    }).as('savePreferences');
    
    // 填写表单
    cy.get('input[name="username"]').type('测试用户');
    cy.get('select[name="mbti"]').select('INFJ');
    cy.get('select[name="tone"]').select('supportive');
    cy.get('input[name="age"]').type('30');
    cy.get('select[name="star_sign"]').select('天秤座');
    
    // 提交表单
    cy.contains('button', '保存并开始聊天').click();
    
    // 等待API请求完成
    cy.wait('@savePreferences');
    
    // 检查是否导航到聊天页面
    cy.url().should('include', '/chat');
  });
}); 