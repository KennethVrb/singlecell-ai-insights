import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

type ClearHistoryDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
}

function ClearHistoryDialog({ open, onOpenChange, onConfirm }: ClearHistoryDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Clear chat history?</DialogTitle>
          <DialogDescription>
            <p>This will permanently delete all messages in this conversation.</p>
            <p>You can start a fresh conversation after clearing.</p>
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button variant="destructive" onClick={onConfirm}>
            Clear history
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export { ClearHistoryDialog }
