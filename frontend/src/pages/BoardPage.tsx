import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
  type DragStartEvent,
  type DragEndEvent,
  type DragOverEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  useSortable,
  horizontalListSortingStrategy,
  verticalListSortingStrategy,
  arrayMove,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import {
  Plus, ArrowLeft, MoreHorizontal, Trash2, GripVertical,
  Clock, AlertCircle, CheckCircle2, X, Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { boardsApi } from "@/api/boards";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { cn, PRIORITY_CONFIG } from "@/lib/utils";
import type { Column, Task } from "@/types";

// ── Task Card ─────────────────────────────────────────────
function TaskCard({
  task,
  onDelete,
  isDragging,
}: {
  task: Task;
  onDelete: (id: string) => void;
  isDragging?: boolean;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging: isSortableDragging } =
    useSortable({ id: task.id, data: { type: "task", task } });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isSortableDragging ? 0.3 : 1,
  };

  const priority = PRIORITY_CONFIG[task.priority as keyof typeof PRIORITY_CONFIG];

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        "bg-background border border-border rounded-lg p-3 group cursor-grab active:cursor-grabbing",
        "hover:border-primary/40 hover:shadow-md transition-all duration-150",
        isDragging && "shadow-2xl border-primary rotate-2"
      )}
    >
      {/* Cover color */}
      {task.cover_color && (
        <div
          className="w-full h-1.5 rounded-full mb-2"
          style={{ backgroundColor: task.cover_color }}
        />
      )}

      <div className="flex items-start justify-between gap-2">
        <div
          {...attributes}
          {...listeners}
          className="flex items-start gap-2 flex-1 min-w-0"
        >
          <GripVertical className="w-3.5 h-3.5 text-muted-foreground mt-0.5 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
          <p className="text-sm text-foreground leading-snug line-clamp-3">{task.title}</p>
        </div>
        <button
          onClick={() => onDelete(task.id)}
          className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 hover:text-destructive flex-shrink-0"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Footer */}
      <div className="flex items-center gap-2 mt-2 flex-wrap">
        {task.priority !== "no_priority" && (
          <span className={cn("text-xs px-1.5 py-0.5 rounded font-medium", priority.bg, priority.color)}>
            {priority.label}
          </span>
        )}
        {task.due_date && (
          <span className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="w-3 h-3" />
            {new Date(task.due_date).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" })}
          </span>
        )}
        {task.is_completed && (
          <CheckCircle2 className="w-3.5 h-3.5 text-green-500 ml-auto" />
        )}
      </div>
    </div>
  );
}

// ── Column Component ──────────────────────────────────────
function KanbanColumn({
  column,
  tasks,
  onAddTask,
  onDeleteTask,
  onDeleteColumn,
  isAddingTask,
}: {
  column: Column;
  tasks: Task[];
  onAddTask: (columnId: string, title: string) => void;
  onDeleteTask: (taskId: string) => void;
  onDeleteColumn: (columnId: string) => void;
  isAddingTask: boolean;
}) {
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [showInput, setShowInput] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const { setNodeRef } = useSortable({
    id: column.id,
    data: { type: "column", column },
  });

  const handleAddTask = () => {
    if (!newTaskTitle.trim()) return;
    onAddTask(column.id, newTaskTitle.trim());
    setNewTaskTitle("");
    setShowInput(false);
  };

  return (
    <div
      ref={setNodeRef}
      className="flex flex-col w-72 flex-shrink-0 bg-muted/50 rounded-xl border border-border"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 pb-2">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: column.color }} />
          <span className="text-sm font-semibold text-foreground">{column.title}</span>
          <span className="text-xs bg-muted text-muted-foreground px-1.5 py-0.5 rounded-full font-medium">
            {tasks.length}
          </span>
        </div>
        <div className="relative">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-1 rounded hover:bg-accent transition-colors text-muted-foreground"
          >
            <MoreHorizontal className="w-4 h-4" />
          </button>
          <AnimatePresence>
            {menuOpen && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9, y: -5 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: -5 }}
                className="absolute right-0 top-7 bg-popover border border-border rounded-lg shadow-xl py-1 z-20 min-w-36"
              >
                <button
                  onClick={() => { onDeleteColumn(column.id); setMenuOpen(false); }}
                  className="flex items-center gap-2 w-full px-3 py-2 text-sm text-destructive hover:bg-destructive/10 transition-colors"
                >
                  <Trash2 className="w-4 h-4" /> Deletar coluna
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Tasks */}
      <div className="flex-1 overflow-y-auto px-2 pb-2 space-y-2 max-h-[calc(100vh-280px)]">
        <SortableContext items={tasks.map((t) => t.id)} strategy={verticalListSortingStrategy}>
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onDelete={onDeleteTask} />
          ))}
        </SortableContext>

        {/* Add task input */}
        <AnimatePresence>
          {showInput && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="space-y-2"
            >
              <textarea
                autoFocus
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleAddTask(); }
                  if (e.key === "Escape") setShowInput(false);
                }}
                placeholder="Título da tarefa..."
                rows={2}
                className="w-full text-sm bg-background border border-border rounded-lg px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-primary text-foreground placeholder:text-muted-foreground"
              />
              <div className="flex gap-2">
                <Button size="sm" onClick={handleAddTask} disabled={!newTaskTitle.trim() || isAddingTask} className="flex-1">
                  {isAddingTask ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : "Adicionar"}
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setShowInput(false)}>
                  <X className="w-3.5 h-3.5" />
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Add task button */}
      {!showInput && (
        <button
          onClick={() => setShowInput(true)}
          className="flex items-center gap-2 m-2 px-3 py-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors text-sm"
        >
          <Plus className="w-4 h-4" /> Adicionar tarefa
        </button>
      )}
    </div>
  );
}

// ── Add Column Modal ──────────────────────────────────────
function AddColumnModal({ boardId, onClose }: { boardId: string; onClose: () => void }) {
  const [title, setTitle] = useState("");
  const [color, setColor] = useState("#6366f1");
  const queryClient = useQueryClient();

  const COLORS = ["#94a3b8", "#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#ec4899", "#06b6d4", "#8b5cf6"];

  const { mutate, isPending } = useMutation({
    mutationFn: () => boardsApi.createColumn(boardId, { title, color, position: 999 }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["columns", boardId] });
      toast.success("Coluna criada!");
      onClose();
    },
    onError: () => toast.error("Erro ao criar coluna"),
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
        className="bg-card border border-border rounded-2xl p-6 w-full max-w-sm shadow-2xl"
      >
        <h2 className="text-lg font-bold text-foreground mb-4">Nova Coluna</h2>
        <div className="space-y-4">
          <Input
            label="Nome"
            placeholder="Ex: Em Revisão, Bloqueado..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && title && mutate()}
            autoFocus
          />
          <div>
            <label className="text-sm font-medium text-foreground block mb-2">Cor</label>
            <div className="flex gap-2 flex-wrap">
              {COLORS.map((c) => (
                <button
                  key={c}
                  onClick={() => setColor(c)}
                  className="w-7 h-7 rounded-full transition-transform hover:scale-110"
                  style={{ backgroundColor: c, outline: color === c ? `3px solid ${c}` : "none", outlineOffset: "2px" }}
                />
              ))}
            </div>
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <Button variant="outline" className="flex-1" onClick={onClose}>Cancelar</Button>
          <Button className="flex-1" onClick={() => mutate()} disabled={!title.trim()} loading={isPending}>
            Criar
          </Button>
        </div>
      </motion.div>
    </motion.div>
  );
}

// ── Main Board Page ───────────────────────────────────────
export function BoardPage() {
  const { boardId } = useParams<{ boardId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [showAddColumn, setShowAddColumn] = useState(false);
  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [localTasks, setLocalTasks] = useState<Record<string, Task[]>>({});
  const [initialized, setInitialized] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } })
  );

  const { data: board, isLoading: boardLoading } = useQuery({
    queryKey: ["board", boardId],
    queryFn: () => boardsApi.get(boardId!),
    enabled: !!boardId,
  });

  const { data: columns = [], isLoading: columnsLoading } = useQuery({
    queryKey: ["columns", boardId],
    queryFn: () => boardsApi.getColumns(boardId!),
    enabled: !!boardId,
  });

  // Fetch tasks for all columns
  const { data: allTasksData = {} } = useQuery({
    queryKey: ["tasks", boardId, columns.map((c) => c.id).join(",")],
    queryFn: async () => {
      const result: Record<string, Task[]> = {};
      await Promise.all(
        columns.map(async (col) => {
          result[col.id] = await boardsApi.getTasks(boardId!, col.id);
        })
      );
      return result;
    },
    enabled: columns.length > 0,
    onSuccess: (data: Record<string, Task[]>) => {
      if (!initialized) {
        setLocalTasks(data);
        setInitialized(true);
      }
    },
  } as any);

  const tasks = initialized ? localTasks : allTasksData;

  const { mutate: addTask, isPending: isAddingTask } = useMutation({
    mutationFn: ({ columnId, title }: { columnId: string; title: string }) =>
      boardsApi.createTask(boardId!, columnId, { title }),
    onSuccess: (newTask, { columnId }) => {
      setLocalTasks((prev) => ({
        ...prev,
        [columnId]: [...(prev[columnId] || []), newTask],
      }));
      queryClient.invalidateQueries({ queryKey: ["tasks", boardId] });
      toast.success("Tarefa criada!");
    },
    onError: () => toast.error("Erro ao criar tarefa"),
  });

  const { mutate: deleteTask } = useMutation({
    mutationFn: (taskId: string) => boardsApi.deleteTask(boardId!, taskId),
    onSuccess: (_, taskId) => {
      setLocalTasks((prev) => {
        const updated = { ...prev };
        for (const colId in updated) {
          updated[colId] = updated[colId].filter((t) => t.id !== taskId);
        }
        return updated;
      });
      toast.success("Tarefa removida");
    },
    onError: () => toast.error("Erro ao remover tarefa"),
  });

  const { mutate: deleteColumn } = useMutation({
    mutationFn: (columnId: string) => boardsApi.deleteColumn(boardId!, columnId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["columns", boardId] });
      toast.success("Coluna removida");
    },
    onError: () => toast.error("Erro ao remover coluna"),
  });

  // Drag handlers
  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    if (active.data.current?.type === "task") {
      setActiveTask(active.data.current.task);
    }
  };

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const activeColId = Object.keys(tasks).find((colId) =>
      tasks[colId]?.some((t) => t.id === activeId)
    );
    const overColId =
      Object.keys(tasks).find((colId) => tasks[colId]?.some((t) => t.id === overId)) ||
      (columns.find((c) => c.id === overId) ? overId : null);

    if (!activeColId || !overColId || activeColId === overColId) return;

    setLocalTasks((prev) => {
      const activeTask = prev[activeColId]?.find((t) => t.id === activeId);
      if (!activeTask) return prev;
      return {
        ...prev,
        [activeColId]: prev[activeColId].filter((t) => t.id !== activeId),
        [overColId]: [...(prev[overColId] || []), { ...activeTask, column_id: overColId }],
      };
    });
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveTask(null);
    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const colId = Object.keys(tasks).find((id) => tasks[id]?.some((t) => t.id === activeId));
    if (!colId) return;

    const colTasks = tasks[colId];
    const oldIndex = colTasks.findIndex((t) => t.id === activeId);
    const newIndex = colTasks.findIndex((t) => t.id === overId);

    if (oldIndex !== newIndex && newIndex !== -1) {
      setLocalTasks((prev) => ({
        ...prev,
        [colId]: arrayMove(prev[colId], oldIndex, newIndex),
      }));
    }

    // Persist move to backend
    boardsApi.updateTask(boardId!, activeId, {
      column_id: colId as any,
      position: newIndex !== -1 ? newIndex : colTasks.length - 1,
    }).catch(() => toast.error("Erro ao mover tarefa"));
  };

  if (boardLoading || columnsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!board) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <AlertCircle className="w-12 h-12 text-muted-foreground" />
        <p className="text-muted-foreground">Board não encontrado</p>
        <Button onClick={() => navigate("/boards")}>Voltar</Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4 px-6 py-4 border-b border-border flex-shrink-0"
      >
        <button
          onClick={() => navigate("/boards")}
          className="p-2 rounded-lg hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center text-lg flex-shrink-0"
          style={{ backgroundColor: board.color + "30" }}
        >
          {board.icon || "📋"}
        </div>
        <div>
          <h1 className="text-lg font-bold text-foreground leading-none">{board.title}</h1>
          {board.description && (
            <p className="text-xs text-muted-foreground mt-0.5">{board.description}</p>
          )}
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span className="text-xs text-muted-foreground">
            {columns.length} colunas · {Object.values(tasks).flat().length} tarefas
          </span>
          <Button size="sm" onClick={() => setShowAddColumn(true)}>
            <Plus className="w-4 h-4" /> Coluna
          </Button>
        </div>
      </motion.div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
        >
          <div className="flex gap-4 p-6 h-full items-start">
            <SortableContext
              items={columns.map((c) => c.id)}
              strategy={horizontalListSortingStrategy}
            >
              <AnimatePresence>
                {columns.map((column, i) => (
                  <motion.div
                    key={column.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    <KanbanColumn
                      column={column}
                      tasks={tasks[column.id] || []}
                      onAddTask={(colId, title) => addTask({ columnId: colId, title })}
                      onDeleteTask={(taskId) => deleteTask(taskId)}
                      onDeleteColumn={(colId) => deleteColumn(colId)}
                      isAddingTask={isAddingTask}
                    />
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Add column button */}
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: columns.length * 0.05 }}
                onClick={() => setShowAddColumn(true)}
                className="flex-shrink-0 w-72 h-14 rounded-xl border-2 border-dashed border-border hover:border-primary/50 hover:bg-primary/5 transition-all flex items-center justify-center gap-2 text-muted-foreground hover:text-primary text-sm font-medium"
              >
                <Plus className="w-4 h-4" /> Nova coluna
              </motion.button>
            </SortableContext>
          </div>

          {/* Drag overlay */}
          <DragOverlay>
            {activeTask && (
              <TaskCard task={activeTask} onDelete={() => {}} isDragging />
            )}
          </DragOverlay>
        </DndContext>
      </div>

      {/* Add Column Modal */}
      <AnimatePresence>
        {showAddColumn && (
          <AddColumnModal boardId={boardId!} onClose={() => setShowAddColumn(false)} />
        )}
      </AnimatePresence>
    </div>
  );
}