import { motion } from "framer-motion";
import { Kanban, Calendar, CheckCircle, Clock } from "lucide-react";
import { useAuthStore } from "@/store/authStore";

const stats = [
  { label: "Boards ativos", value: "0", icon: Kanban, color: "text-blue-500", bg: "bg-blue-500/10" },
  { label: "Tarefas hoje", value: "0", icon: CheckCircle, color: "text-green-500", bg: "bg-green-500/10" },
  { label: "Eventos esta semana", value: "0", icon: Calendar, color: "text-purple-500", bg: "bg-purple-500/10" },
  { label: "Em progresso", value: "0", icon: Clock, color: "text-orange-500", bg: "bg-orange-500/10" },
];

export function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold text-foreground">
          Olá, {user?.full_name?.split(" ")[0]} 👋
        </h1>
        <p className="text-muted-foreground mt-1">
          Aqui está o resumo do seu dia
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-card border border-border rounded-xl p-5"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <p className="text-3xl font-bold text-foreground mt-1">
                  {stat.value}
                </p>
              </div>
              <div className={`w-12 h-12 rounded-lg ${stat.bg} flex items-center justify-center`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Placeholder para próximas phases */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="bg-card border border-border rounded-xl p-8 text-center"
      >
        <Kanban className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
        <h3 className="font-semibold text-foreground">Kanban Board</h3>
        <p className="text-sm text-muted-foreground mt-1">
          Phase 4 — em breve seus boards aparecerão aqui
        </p>
      </motion.div>
    </div>
  );
}
