// ============================================================
// data-utils.js - 统一数据源工具
// 三端共用，确保数据一致
// ============================================================

// ---------- 密码管理 ----------
function getPasswords() {
    const saved = localStorage.getItem('app_passwords');
    if (saved) {
        try { return JSON.parse(saved); } catch(e) {}
    }
    const defaults = { student: 'student123', teacher: 'teacher123', admin: 'admin123' };
    localStorage.setItem('app_passwords', JSON.stringify(defaults));
    return defaults;
}

function getPassword(role) {
    const passwords = getPasswords();
    return passwords[role] || null;
}

function setPassword(role, newPwd) {
    const passwords = getPasswords();
    passwords[role] = newPwd;
    localStorage.setItem('app_passwords', JSON.stringify(passwords));
}

// ---------- 教师数据（唯一数据源） ----------
function getDefaultTeacherData() {
    return {
        teacher_name: '张老师',
        current_class: '英语2023-1班',
        classes: {
            '英语2023-1班': {
                school: '天津农学院',
                students: ['张三', '李四', '王五', '赵六'],
                tasks: [
                    { 
                        id: 't1', 
                        title: '环境保护的重要性', 
                        requirement: 'Write a 200-word essay on the importance of environmental protection. Discuss at least three reasons why we should protect the environment and provide examples.', 
                        deadline: '2026-07-30', 
                        status: 'active' 
                    },
                    { 
                        id: 't2', 
                        title: '人工智能的影响', 
                        requirement: 'Write a 250-word essay discussing the impact of artificial intelligence on our daily lives. Include both positive and negative aspects.', 
                        deadline: '2026-08-05', 
                        status: 'active' 
                    }
                ],
                submissions: {}
            },
            '英语2023-2班': {
                school: '天津农学院',
                students: ['钱七', '孙八', '周九', '吴十'],
                tasks: [
                    { 
                        id: 't3', 
                        title: '文化多样性的价值', 
                        requirement: 'Write a 200-word essay on the value of cultural diversity. Explain why it is important to preserve different cultures and traditions.', 
                        deadline: '2026-08-12', 
                        status: 'active' 
                    }
                ],
                submissions: {}
            }
        }
    };
}

function getTeacherData() {
    const saved = localStorage.getItem('teacher_data');
    if (saved) {
        try { 
            const data = JSON.parse(saved);
            if (!data.classes) {
                data.classes = getDefaultTeacherData().classes;
            }
            return data;
        } catch(e) {}
    }
    const defaults = getDefaultTeacherData();
    localStorage.setItem('teacher_data', JSON.stringify(defaults));
    return defaults;
}

function saveTeacherData(data) {
    localStorage.setItem('teacher_data', JSON.stringify(data));
}

// ---------- 班级数据（从 teacher_data 派生） ----------
function getCurrentClassData() {
    const teacherData = getTeacherData();
    const className = teacherData.current_class || Object.keys(teacherData.classes)[0] || '';
    return {
        className: className,
        classData: teacherData.classes[className] || { students: [], tasks: [], submissions: {} },
        teacherName: teacherData.teacher_name || '张老师'
    };
}

function getClassData(className) {
    const teacherData = getTeacherData();
    if (!teacherData.classes[className]) {
        teacherData.classes[className] = {
            school: '天津农学院',
            students: [],
            tasks: [],
            submissions: {}
        };
        saveTeacherData(teacherData);
    }
    return teacherData.classes[className];
}

function getStudentNames(className) {
    const classData = getClassData(className);
    return classData.students || [];
}

function getTasks(className) {
    const classData = getClassData(className);
    return classData.tasks || [];
}

function getSubmissions(className) {
    const classData = getClassData(className);
    return classData.submissions || {};
}

function getAllClassNames() {
    const teacherData = getTeacherData();
    return Object.keys(teacherData.classes || {});
}

// ---------- 核心：学生提交同步（写入 teacher_data） ----------
function syncStudentSubmission(className, studentName, submissionData) {
    const teacherData = getTeacherData();
    if (!teacherData.classes[className]) {
        teacherData.classes[className] = {
            school: '天津农学院',
            students: [],
            tasks: [],
            submissions: {}
        };
    }
    if (!teacherData.classes[className].submissions) {
        teacherData.classes[className].submissions = {};
    }
    teacherData.classes[className].submissions[studentName] = submissionData;
    saveTeacherData(teacherData);
}

// ---------- 教师端：发布任务 ----------
function publishTaskToClass(className, taskData) {
    const teacherData = getTeacherData();
    if (!teacherData.classes[className]) {
        teacherData.classes[className] = {
            school: '天津农学院',
            students: [],
            tasks: [],
            submissions: {}
        };
    }
    teacherData.classes[className].tasks.push(taskData);
    saveTeacherData(teacherData);
}

// ---------- 教师端：删除任务 ----------
function deleteTaskFromClass(className, taskId) {
    const teacherData = getTeacherData();
    if (teacherData.classes[className]) {
        teacherData.classes[className].tasks = teacherData.classes[className].tasks.filter(t => t.id !== taskId);
        saveTeacherData(teacherData);
    }
}

// ---------- 教师端：添加学生 ----------
function addStudentToClass(className, studentName) {
    const teacherData = getTeacherData();
    if (!teacherData.classes[className]) {
        teacherData.classes[className] = {
            school: '天津农学院',
            students: [],
            tasks: [],
            submissions: {}
        };
    }
    if (!teacherData.classes[className].students.includes(studentName)) {
        teacherData.classes[className].students.push(studentName);
        saveTeacherData(teacherData);
        return true;
    }
    return false;
}

// ---------- 教师端：移除学生 ----------
function removeStudentFromClass(className, studentName) {
    const teacherData = getTeacherData();
    if (teacherData.classes[className]) {
        teacherData.classes[className].students = teacherData.classes[className].students.filter(s => s !== studentName);
        // 同时删除该学生的提交记录
        if (teacherData.classes[className].submissions) {
            delete teacherData.classes[className].submissions[studentName];
        }
        saveTeacherData(teacherData);
        return true;
    }
    return false;
}

// ---------- 教师端：切换班级 ----------
function switchClass(className) {
    const teacherData = getTeacherData();
    if (teacherData.classes[className]) {
        teacherData.current_class = className;
        saveTeacherData(teacherData);
        return true;
    }
    return false;
}

// ---------- 教师端：获取提交学生列表（有提交记录的学生） ----------
function getSubmittedStudents(className) {
    const submissions = getSubmissions(className);
    const students = getStudentNames(className);
    return students.filter(name => {
        const sub = submissions[name];
        return sub && sub.original && sub.original.trim().length > 0;
    });
}

// ---------- 初始化默认数据（兼容旧版） ----------
function initDefaultData() {
    const teacherData = getTeacherData();
    // 如果 classes 为空，填充默认
    if (!teacherData.classes || Object.keys(teacherData.classes).length === 0) {
        const defaults = getDefaultTeacherData();
        teacherData.classes = defaults.classes;
        teacherData.current_class = defaults.current_class;
        saveTeacherData(teacherData);
    }
}

// 自动初始化
initDefaultData();