import { useEffect, useState, type FormEvent } from "react";
import { format, parseISO } from "date-fns";
import { PlusIcon, VoteIcon } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/components/ui/empty";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { getErrorMessage } from "@/services/api";
import { createPoll, listPolls } from "@/services/pollService";
import type { Poll } from "@/types/poll";

const toOptions = (text: string) => text.split("\n").map((s) => s.trim()).filter(Boolean);

export default function Polls() {
  const [polls, setPolls] = useState<Poll[] | null>(null);
  const [question, setQuestion] = useState("");
  const [optionsText, setOptionsText] = useState("");
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    listPolls()
      .then(setPolls)
      .catch((err) => {
        setPolls([]);
        toast.error(getErrorMessage(err, "Could not load polls."), { id: "load-polls" });
      });
  }, []);

  function openDialog() {
    setQuestion("");
    setOptionsText("");
    setOpen(true);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const saved = await createPoll({ question, options: toOptions(optionsText) });
      setPolls((prev) => [saved, ...(prev ?? [])]);
      setOpen(false);
      toast.success("Poll created.");
    } catch (err) {
      toast.error(getErrorMessage(err, "Could not create the poll."));
    } finally {
      setSaving(false);
    }
  }

  const complete = question.trim() && toOptions(optionsText).length >= 2;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-heading text-2xl">Polls</CardTitle>
        <CardDescription>{polls ? `${polls.length} polls` : "Loading..."}</CardDescription>
        <CardAction>
          <Button onClick={openDialog}>
            <PlusIcon data-icon="inline-start" />
            New
          </Button>
        </CardAction>
      </CardHeader>

      <CardContent>
        {!polls ? (
          <div className="flex flex-col gap-3" aria-busy="true">
            {[0, 1, 2].map((i) => (
              <Skeleton key={i} className="h-9 w-full" />
            ))}
          </div>
        ) : polls.length === 0 ? (
          <Empty>
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <VoteIcon />
              </EmptyMedia>
              <EmptyTitle>No polls yet</EmptyTitle>
              <EmptyDescription>Create the first poll with the New button.</EmptyDescription>
            </EmptyHeader>
          </Empty>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Question</TableHead>
                <TableHead>Options</TableHead>
                <TableHead>Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {polls.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium whitespace-normal">{p.question}</TableCell>
                  <TableCell>{p.options.length}</TableCell>
                  <TableCell>{format(parseISO(p.created_at), "yyyy-MM-dd HH:mm")}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <DialogHeader>
              <DialogTitle>New poll</DialogTitle>
            </DialogHeader>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="poll-question">Question</FieldLabel>
                <Input
                  id="poll-question"
                  required
                  maxLength={200}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="poll-options">Options</FieldLabel>
                <Textarea
                  id="poll-options"
                  rows={5}
                  value={optionsText}
                  onChange={(e) => setOptionsText(e.target.value)}
                />
                <FieldDescription>One option per line, at least 2.</FieldDescription>
              </Field>
            </FieldGroup>
            <DialogFooter>
              <Button type="submit" disabled={saving || !complete}>
                {saving && <Spinner data-icon="inline-start" />}
                Create
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
