import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Mail, Lock, User, AtSign, LayoutDashboard } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { authApi } from "@/api/auth";

const registerSchema = z.object({
  full_name: z.string().min(2, "Nome deve ter pelo menos 2 caracteres"),
  username: z
    .string()
    .min(3, "Username deve ter pelo menos 3 caracteres")
    .regex(/^[a-zA-Z0-9_]+$/, "Apenas letras, números e _"),
  email: z.string().email("Email inválido"),
  password: z
    .string()
    .min(8, "Senha deve ter pelo menos 8 caracteres"),
});

type RegisterForm = z.infer<typeof registerSchema>;

export function RegisterPage() {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterForm) => {
    try {
      await authApi.register(data);
      toast.success("Conta criada! Faça login para continuar.");
      navigate("/login");
    } catch {
      toast.error("Erro ao criar conta. Tente novamente.");
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-background" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative w-full max-w-md"
      >
        <div className="bg-card border border-border rounded-xl shadow-lg p-8 space-y-6">

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">FlowBoard</h1>
              <p className="text-xs text-muted-foreground">Produtividade profissional</p>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-foreground">Criar conta</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Comece sua jornada de produtividade
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="Nome completo"
              placeholder="João Silva"
              leftIcon={<User className="w-4 h-4" />}
              error={errors.full_name?.message}
              {...register("full_name")}
            />

            <Input
              label="Username"
              placeholder="joaosilva"
              leftIcon={<AtSign className="w-4 h-4" />}
              error={errors.username?.message}
              {...register("username")}
            />

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
              placeholder="Mínimo 8 caracteres"
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
              Criar conta
            </Button>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            Já tem uma conta?{" "}
            <Link to="/login" className="text-primary hover:underline font-medium">
              Entrar
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
