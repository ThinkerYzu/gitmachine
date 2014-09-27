gitmachine is a tool to implement a backup storage that like Apple
Time Machine.  It hacks git repositories to remove all commits before
a given commit from the repository.  Then, you could purge old commits
from the repository before using up your storage.

> # A full sha1 code
> $ python /path/to/gitmachine.py 859a03f738a462197a96e2ae53b7d390d3f6dc75
> $ git prune
> 

gitmachine would create fake commits to replace the content of parents
of the given commit, so all ancester commits are removed from the
tree.  Although those commits are removed from the tree, they are
still in the repository.  |git prune| would remove them since they are
not reachable.
