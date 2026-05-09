// ============================================================
// FlowBoard — Login Page
// Formulário com React Hook Form + Zod + Framer Motion
// ============================================================

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Mail, Lock, LayoutDashboard } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/store/authStore";

// Schema de validação Zod
const loginSchema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(1, "Senha obrigatória"),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      // 1. Fazer login e obter tokens
      const tokens = await authApi.login(data);

      // 2. Buscar dados do usuário
      localStorage.setItem("access_token", tokens.access_token);
      const user = await authApi.getMe();

      // 3. Salvar no estado global
      setAuth(user, tokens.access_token, tokens.refresh_token);

      toast.success(`Bem-vindo, ${user.full_name}! 👋`);
      navigate("/dashboard");
    } catch {
      toast.error("Email ou senha incorretos");
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      {/* Background gradient animado */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-background" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative w-full max-w-md"
      >
        {/* Card */}
        <div className="bg-card border border-border rounded-xl shadow-lg p-8 space-y-6">

          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="flex items-center gap-3 mb-2"
          >
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">FlowBoard</h1>
              <p className="text-xs text-muted-foreground">Produtividade profissional</p>
            </div>
          </motion.div>

          {/* Header */}
          <div>
            <h2 className="text-2xl font-bold text-foreground">Entrar</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Acesse seu workspace
            </p>
          </div>

          {/* Formulário */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Email"
              type="email"
              placeholder="seu@email.com"
              leftIcon={<Mail className="w-4 h-4" />}
              error={errors.email?.message}
              {...register("email")}
            />

            <Input
              label="Senha"
              type="password"
              placeholder="••••••••"
              leftIcon={<Lock className="w-4 h-4" />}
              error={errors.password?.message}
              {...register("password")}
            />

            <Button
              type="submit"
              className="w-full"
              loading={isSubmitting}
              size="lg"
            >
              Entrar
            </Button>
          </form>

          {/* Link para registro */}
          <p className="text-center text-sm text-muted-foreground">
            Não tem uma conta?{" "}
            <Link
              to="/register"
              className="text-primary hover:underline font-medium"
            >
              Criar conta
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
