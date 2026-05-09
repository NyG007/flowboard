import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Kanban, MoreHorizontal, Trash2, Archive, Globe, Lock } from "lucide-react";
import { toast } from "sonner";
import { boardsApi } from "@/api/boards";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import type { Board } from "@/types";
import { formatDate } from "@/lib/utils";

const BOARD_COLORS = [
  "#3b82f6", "#8b5cf6", "#ec4899", "#f59e0b",
  "#10b981", "#ef4444", "#06b6d4", "#f97316",
];

function CreateBoardModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [color, setColor] = useState(BOARD_COLORS[0]);
  const [isPublic, setIsPublic] = useState(false);

  const { mutate, isPending } = useMutation({
    mutationFn: () => boardsApi.create({ title, color, is_public: isPublic }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["boards"] });
      toast.success("Board criado!");
      onClose();
    },
    onError: () => toast.error("Erro ao criar board"),
  });

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-card border border-border rounded-2xl p-6 w-full max-w-md shadow-2xl"
      >
        <h2 className="text-xl font-bold text-foreground mb-6">Novo Board</h2>

        {/* Preview */}
        <div
          className="w-full h-24 rounded-xl mb-6 flex items-center justify-center"
          style={{ backgroundColor: color + "20", border: `2px solid ${color}40` }}
        >
          <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: color }}>
            <Kanban className="w-5 h-5 text-white" />
          </div>
        </div>

        <div className="space-y-4">
          <Input
            label="Nome do board"
            placeholder="Ex: Marketing Q2, Sprint 14..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && title && mutate()}
            autoFocus
          />

          {/* Color picker */}
          <div>
            <label className="text-sm font-medium text-foreground block mb-2">Cor</label>
            <div className="flex gap-2 flex-wrap">
              {BOARD_COLORS.map((c) => (
                <button
                  key={c}
                  onClick={() => setColor(c)}
                  className="w-8 h-8 rounded-full transition-transform hover:scale-110"
                  style={{
                    backgroundColor: c,
                    outline: color === c ? `3px solid ${c}` : "none",
                    outlineOffset: "2px",
                  }}
                />
              ))}
            </div>
          </div>

          {/* Visibility */}
          <button
            onClick={() => setIsPublic(!isPublic)}
            className="flex items-center gap-3 w-full p-3 rounded-lg border border-border hover:border-primary/50 transition-colors"
          >
            {isPublic ? (
              <Globe className="w-4 h-4 text-primary" />
            ) : (
              <Lock className="w-4 h-4 text-muted-foreground" />
            )}
            <div className="text-left">
              <p className="text-sm font-medium text-foreground">
                {isPublic ? "Público" : "Privado"}
              </p>
              <p className="text-xs text-muted-foreground">
                {isPublic ? "Qualquer membro pode ver" : "Apenas você"}
              </p>
            </div>
            <div className={`ml-auto w-10 h-5 rounded-full transition-colors ${isPublic ? "bg-primary" : "bg-muted"}`}>
              <motion.div
                animate={{ x: isPublic ? 20 : 2 }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
                className="w-4 h-4 bg-white rounded-full mt-0.5 shadow"
              />
            </div>
          </button>
        </div>

        <div className="flex gap-3 mt-6">
          <Button variant="outline" className="flex-1" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            className="flex-1"
            onClick={() => mutate()}
            disabled={!title.trim()}
            loading={isPending}
          >
            Criar Board
          </Button>
        </div>
      </motion.div>
    </motion.div>
  );
}

function BoardCard({ board, onDelete }: { board: Board; onDelete: (id: string) => void }) {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
      className="bg-card border border-border rounded-xl overflow-hidden cursor-pointer group relative"
      onClick={() => navigate(`/boards/${board.id}`)}
    >
      {/* Color header */}
      <div
        className="h-20 flex items-center justify-center relative"
        style={{ backgroundColor: board.color + "30" }}
      >
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg"
          style={{ backgroundColor: board.color }}
        >
          <span className="text-2xl">{board.icon || "📋"}</span>
        </div>

        {/* Menu button */}
        <button
          onClick={(e) => { e.stopPropagation(); setMenuOpen(!menuOpen); }}
          className="absolute top-2 right-2 w-7 h-7 rounded-lg bg-black/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/40"
        >
          <MoreHorizontal className="w-4 h-4 text-white" />
        </button>

        {/* Dropdown menu */}
        <AnimatePresence>
          {menuOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: -5 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -5 }}
              onClick={(e) => e.stopPropagation()}
              className="absolute top-10 right-2 bg-popover border border-border rounded-lg shadow-xl py-1 z-10 min-w-36"
            >
              <button className="flex items-center gap-2 w-full px-3 py-2 text-sm text-foreground hover:bg-accent transition-colors">
                <Archive className="w-4 h-4" /> Arquivar
              </button>
              <button
                onClick={() => onDelete(board.id)}
                className="flex items-center gap-2 w-full px-3 py-2 text-sm text-destructive hover:bg-destructive/10 transition-colors"
              >
                <Trash2 className="w-4 h-4" /> Deletar
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="font-semibold text-foreground truncate">{board.title}</h3>
        {board.description && (
          <p className="text-xs text-muted-foreground mt-1 truncate">{board.description}</p>
        )}
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-muted-foreground">{formatDate(board.created_at)}</span>
          {board.is_public ? (
            <Globe className="w-3.5 h-3.5 text-muted-foreground" />
          ) : (
            <Lock className="w-3.5 h-3.5 text-muted-foreground" />
          )}
        </div>
      </div>
    </motion.div>
  );
}

export function BoardsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const queryClient = useQueryClient();

  const { data: boards = [], isLoading } = useQuery({
    queryKey: ["boards"],
    queryFn: boardsApi.list,
  });

  const { mutate: deleteBoard } = useMutation({
    mutationFn: boardsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["boards"] });
      toast.success("Board deletado");
    },
    onError: () => toast.error("Erro ao deletar board"),
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold text-foreground">Meus Boards</h1>
          <p className="text-muted-foreground text-sm mt-1">
            {boards.length} board{boards.length !== 1 ? "s" : ""}
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4" /> Novo Board
        </Button>
      </motion.div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-card border border-border rounded-xl h-40 animate-pulse" />
          ))}
        </div>
      ) : boards.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center justify-center py-24 text-center"
        >
          <div className="w-16 h-16 bg-muted rounded-2xl flex items-center justify-center mb-4">
            <Kanban className="w-8 h-8 text-muted-foreground" />
          </div>
          <h3 className="font-semibold text-foreground text-lg">Nenhum board ainda</h3>
          <p className="text-muted-foreground text-sm mt-1 max-w-xs">
            Crie seu primeiro board para começar a organizar seu trabalho
          </p>
          <Button className="mt-6" onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4" /> Criar primeiro board
          </Button>
        </motion.div>
      ) : (
        <motion.div
          layout
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
        >
          <AnimatePresence>
            {boards.map((board) => (
              <BoardCard key={board.id} board={board} onDelete={deleteBoard} />
            ))}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Modal */}
      <AnimatePresence>
        {showCreate && <CreateBoardModal onClose={() => setShowCreate(false)} />}
      </AnimatePresence>
    </div>
  );
}