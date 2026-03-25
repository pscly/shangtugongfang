import {
  AppstoreOutlined,
  CreditCardOutlined,
  DashboardOutlined,
  LockOutlined,
  ProductOutlined,
} from "@ant-design/icons";
import {
  Alert,
  App as AntApp,
  Button,
  Card,
  ConfigProvider,
  Form,
  Input,
  Layout,
  Menu,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
} from "antd";
import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { BrowserRouter, Link, Navigate, Outlet, Route, Routes, useLocation, useNavigate } from "react-router-dom";

import { AuthState, clearAuthState, loadAuthState, saveAuthState } from "./auth";
import { api, unwrap } from "../services/api";

const { Header, Content, Sider } = Layout;
const queryClient = new QueryClient();

type BackendUser = {
  id: string;
  username: string;
  email: string;
  is_system_admin: boolean;
};

type BackendWorkspace = {
  id: string;
  name: string;
  role: string;
};

type AuthPayload = {
  access_token: string;
  user: BackendUser;
  workspace: BackendWorkspace | null;
};

type WalletPayload = {
  balance: number;
  frozen_balance: number;
};

type ProductPayload = {
  id: string;
  name: string;
  product_type: string;
  notes?: string;
  status: string;
};

type PromptPayload = {
  id: string;
  platform: string;
  category: string;
  draft: Record<string, unknown>;
};

type JobPayload = {
  id: string;
  status: string;
  credits_estimated: number;
  credits_frozen: number;
};

type CardPayload = {
  id: string;
  card_code: string;
  credits_amount: number;
  status: string;
};

type BatchPayload = {
  id: string;
  name: string;
  credits_amount: number;
  total_count: number;
  cards: CardPayload[];
};

type RegisterFormValues = {
  username: string;
  email: string;
  password: string;
  workspaceName: string;
};

type LoginFormValues = {
  username: string;
  password: string;
};

function useAuth() {
  const [authState, setAuthState] = useState<AuthState | null>(() => loadAuthState());

  const setAuth = (value: AuthState | null) => {
    setAuthState(value);
    if (value) {
      saveAuthState(value);
    } else {
      clearAuthState();
    }
  };

  return {
    authState,
    setAuth,
  };
}

function LoginPage({ onAuth }: { onAuth: (state: AuthState) => void }) {
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleRegister = async (values: RegisterFormValues) => {
    try {
      setError(null);
      const data = await unwrap<AuthPayload>(
        api.post("/api/auth/register", {
          username: values.username,
          email: values.email,
          password: values.password,
          workspace_name: values.workspaceName,
        }),
      );
      onAuth({
        accessToken: data.access_token,
        user: {
          id: data.user.id,
          username: data.user.username,
          email: data.user.email,
          isSystemAdmin: data.user.is_system_admin,
        },
        workspace: data.workspace
          ? {
              id: data.workspace.id,
              name: data.workspace.name,
              role: data.workspace.role,
            }
          : null,
      });
      navigate("/");
    } catch (err) {
      setError("注册失败，请检查用户名、邮箱或服务状态。");
    }
  };

  const handleLogin = async (values: LoginFormValues) => {
    try {
      setError(null);
      const data = await unwrap<AuthPayload>(api.post("/api/auth/login", values));
      onAuth({
        accessToken: data.access_token,
        user: {
          id: data.user.id,
          username: data.user.username,
          email: data.user.email,
          isSystemAdmin: data.user.is_system_admin,
        },
        workspace: data.workspace
          ? {
              id: data.workspace.id,
              name: data.workspace.name,
              role: data.workspace.role,
            }
          : null,
      });
      navigate("/");
    } catch (err) {
      setError("登录失败，请检查账号密码。");
    }
  };

  return (
    <Layout style={{ minHeight: "100vh", background: "linear-gradient(135deg, #f3efe6, #e5efe9)" }}>
      <Content style={{ display: "grid", placeItems: "center", padding: 24 }}>
        <Space direction="vertical" size={24} style={{ width: "100%", maxWidth: 1080 }}>
          <Typography.Title style={{ margin: 0 }}>尚图工坊</Typography.Title>
          <Typography.Paragraph style={{ marginTop: 0, maxWidth: 720 }}>
            面向电商团队的图文视频素材工厂。当前版本已打通注册、工作区、积分充值、提示词草稿和任务提交主链路。
          </Typography.Paragraph>
          {error ? <Alert type="error" showIcon message={error} /> : null}
          <Space align="start" size={24} style={{ width: "100%" }}>
            <Card title="注册并创建工作区" style={{ flex: 1 }}>
              <Form layout="vertical" onFinish={handleRegister}>
                <Form.Item label="用户名" name="username" rules={[{ required: true }]}>
                  <Input />
                </Form.Item>
                <Form.Item label="邮箱" name="email" rules={[{ required: true }]}>
                  <Input />
                </Form.Item>
                <Form.Item label="密码" name="password" rules={[{ required: true }]}>
                  <Input.Password />
                </Form.Item>
                <Form.Item label="工作区名称" name="workspaceName" rules={[{ required: true }]}>
                  <Input />
                </Form.Item>
                <Button type="primary" htmlType="submit" block>
                  立即创建
                </Button>
              </Form>
            </Card>
            <Card title="已有账号登录" style={{ flex: 1 }}>
              <Form layout="vertical" onFinish={handleLogin}>
                <Form.Item label="用户名" name="username" rules={[{ required: true }]}>
                  <Input />
                </Form.Item>
                <Form.Item label="密码" name="password" rules={[{ required: true }]}>
                  <Input.Password />
                </Form.Item>
                <Button type="default" htmlType="submit" icon={<LockOutlined />} block>
                  登录进入
                </Button>
              </Form>
            </Card>
          </Space>
        </Space>
      </Content>
    </Layout>
  );
}

function RequireAuth({ auth }: { auth: AuthState | null }) {
  const location = useLocation();
  if (!auth) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <Outlet />;
}

function DashboardLayout({ auth, onLogout }: { auth: AuthState; onLogout: () => void }) {
  const location = useLocation();
  const navigate = useNavigate();
  const items = useMemo(
    () => [
      { key: "/", icon: <DashboardOutlined />, label: <Link to="/">总览</Link> },
      { key: "/products", icon: <ProductOutlined />, label: <Link to="/products">商品工作台</Link> },
      { key: "/credits", icon: <CreditCardOutlined />, label: <Link to="/credits">积分中心</Link> },
      ...(auth.user.isSystemAdmin
        ? [
            {
              key: "/admin/recharge-cards",
              icon: <AppstoreOutlined />,
              label: <Link to="/admin/recharge-cards">管理员后台</Link>,
            },
          ]
        : []),
    ],
    [auth.user.isSystemAdmin],
  );

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider width={240} theme="light">
        <div style={{ padding: 24 }}>
          <Typography.Title level={4} style={{ marginBottom: 4 }}>
            尚图工坊
          </Typography.Title>
          <Typography.Text type="secondary">{auth.workspace?.name ?? "系统管理员"}</Typography.Text>
        </div>
        <Menu selectedKeys={[location.pathname]} mode="inline" items={items} />
      </Sider>
      <Layout>
        <Header
          style={{
            background: "#fff",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            paddingInline: 24,
          }}
        >
          <Space>
            <Tag color="blue">{auth.user.username}</Tag>
            {auth.workspace ? <Tag>{auth.workspace.role}</Tag> : null}
          </Space>
          <Button
            onClick={() => {
              onLogout();
              navigate("/login");
            }}
          >
            退出登录
          </Button>
        </Header>
        <Content style={{ padding: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}

function OverviewPage() {
  const walletQuery = useQuery({
    queryKey: ["wallet-balance"],
    queryFn: () => unwrap<WalletPayload>(api.get("/api/credits/balance")),
  });

  return (
    <Space direction="vertical" size={24} style={{ width: "100%" }}>
      <Typography.Title level={2}>总览</Typography.Title>
      <Space size={16} wrap>
        <Card>
          <Statistic title="可用积分" value={walletQuery.data?.balance ?? 0} loading={walletQuery.isLoading} />
        </Card>
        <Card>
          <Statistic
            title="冻结积分"
            value={walletQuery.data?.frozen_balance ?? 0}
            loading={walletQuery.isLoading}
          />
        </Card>
      </Space>
    </Space>
  );
}

function ProductsPage() {
  const [form] = Form.useForm();
  const [promptDraft, setPromptDraft] = useState<PromptPayload | null>(null);
  const [jobResult, setJobResult] = useState<JobPayload | null>(null);

  const handleCreateProduct = async () => {
    const values = await form.validateFields();
    const product = await unwrap<ProductPayload>(
      api.post("/api/products", {
        name: values.name,
        product_type: values.productType,
        notes: values.notes,
      }),
    );
    const prompt = await unwrap<PromptPayload>(
      api.post("/api/prompt-drafts/compile", {
        product_id: product.id,
        platform: values.platform,
        category: values.category,
        controls: { style: values.style },
      }),
    );
    setPromptDraft(prompt);
    const job = await unwrap<JobPayload>(
      api.post("/api/jobs", {
        product_id: product.id,
        platform: values.platform,
        items: [
          {
            category: values.category,
            count: values.count,
            size: values.size,
            flags: ["upscale"],
            model_key: values.category === "video_scene" ? "openai:sora-2" : "openai:gpt-image-1",
            prompt_draft_id: prompt.id,
          },
        ],
      }),
    );
    setJobResult(job);
  };

  return (
    <Space direction="vertical" size={24} style={{ width: "100%" }}>
      <Typography.Title level={2}>商品工作台</Typography.Title>
      <Card title="创建商品并发起生产">
        <Form
          layout="vertical"
          form={form}
          initialValues={{ platform: "douyin", category: "scene_image", count: 2, size: "m" }}
        >
          <Form.Item label="商品名称" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="商品类型" name="productType" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="备注" name="notes">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item label="平台" name="platform" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="产物分类" name="category" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="风格描述" name="style">
            <Input />
          </Form.Item>
          <Form.Item label="数量" name="count" rules={[{ required: true }]}>
            <Input type="number" />
          </Form.Item>
          <Form.Item label="尺寸档位" name="size" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Button type="primary" onClick={handleCreateProduct}>
            创建并提交任务
          </Button>
        </Form>
      </Card>
      {promptDraft ? (
        <Card title="PromptDraft">
          <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{JSON.stringify(promptDraft, null, 2)}</pre>
        </Card>
      ) : null}
      {jobResult ? (
        <Card title="任务结果">
          <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{JSON.stringify(jobResult, null, 2)}</pre>
        </Card>
      ) : null}
    </Space>
  );
}

function CreditsPage() {
  const walletQuery = useQuery({
    queryKey: ["credits-balance"],
    queryFn: () => unwrap<WalletPayload>(api.get("/api/credits/balance")),
  });

  const [cardCode, setCardCode] = useState("");
  const [lastRedeem, setLastRedeem] = useState<Record<string, unknown> | null>(null);

  const handleRedeem = async () => {
    const data = await unwrap<Record<string, unknown>>(
      api.post("/api/credits/recharge-cards/redeem", { card_code: cardCode }),
    );
    setLastRedeem(data);
    await walletQuery.refetch();
  };

  return (
    <Space direction="vertical" size={24} style={{ width: "100%" }}>
      <Typography.Title level={2}>积分中心</Typography.Title>
      <Card>
        <Space size={24}>
          <Statistic title="可用积分" value={walletQuery.data?.balance ?? 0} />
          <Statistic title="冻结积分" value={walletQuery.data?.frozen_balance ?? 0} />
        </Space>
      </Card>
      <Card title="兑换充值卡">
        <Space.Compact style={{ width: "100%" }}>
          <Input value={cardCode} onChange={(event) => setCardCode(event.target.value)} placeholder="输入卡密" />
          <Button type="primary" onClick={handleRedeem}>
            立即兑换
          </Button>
        </Space.Compact>
        {lastRedeem ? (
          <pre style={{ whiteSpace: "pre-wrap", marginTop: 16 }}>{JSON.stringify(lastRedeem, null, 2)}</pre>
        ) : null}
      </Card>
    </Space>
  );
}

function AdminRechargeCardsPage() {
  const [created, setCreated] = useState<BatchPayload[]>([]);

  const handleCreate = async () => {
    const data = await unwrap<BatchPayload>(
      api.post("/api/admin/recharge-card-batches", {
        name: `批次-${Date.now()}`,
        credits_amount: 200,
        total_count: 3,
      }),
    );
    setCreated((prev) => [data, ...prev]);
  };

  return (
    <Space direction="vertical" size={24} style={{ width: "100%" }}>
      <Typography.Title level={2}>管理员充值卡后台</Typography.Title>
      <Card
        title="创建充值卡批次"
        extra={
          <Button type="primary" onClick={handleCreate}>
            生成 3 张测试卡
          </Button>
        }
      >
        <Table
          rowKey={(record) => String(record.id)}
          dataSource={created}
          pagination={false}
          columns={[
            { title: "批次名", dataIndex: "name" },
            { title: "单卡积分", dataIndex: "credits_amount" },
            { title: "数量", dataIndex: "total_count" },
            {
              title: "卡密预览",
              render: (_, record) =>
                record.cards.map((card) => <Tag key={card.id}>{card.card_code}</Tag>),
            },
          ]}
        />
      </Card>
    </Space>
  );
}

function AppShell() {
  const { authState, setAuth } = useAuth();

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#295f4e",
          borderRadius: 10,
        },
      }}
    >
      <AntApp>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage onAuth={setAuth} />} />
            <Route element={<RequireAuth auth={authState} />}>
              <Route
                element={authState ? <DashboardLayout auth={authState} onLogout={() => setAuth(null)} /> : null}
              >
                <Route path="/" element={<OverviewPage />} />
                <Route path="/products" element={<ProductsPage />} />
                <Route path="/credits" element={<CreditsPage />} />
                <Route path="/admin/recharge-cards" element={<AdminRechargeCardsPage />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  );
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppShell />
    </QueryClientProvider>
  );
}
