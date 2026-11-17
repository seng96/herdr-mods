// Personal Herdr panel adapter. Agent launches and agent commands remain native.
import { exec as nativeExec, watchFolder as nativeWatchFolder, home } from "herdr";

export function wslPath(value) {
  if (typeof value !== "string") return null;
  const normalized = value.replace(/\\/g, "/").replace(/^\/\/\?\/UNC\//i, "//");
  const found = /^\/\/(?:wsl\$|wsl\.localhost)\/([^/]+)(\/.*)?$/i.exec(normalized);
  return found ? { distro: found[1], path: found[2] || "/" } : null;
}

function windowsPath(path, target) {
  return path.startsWith("/") ? `//wsl$/${target.distro}${path}` : path;
}

export function normalizeFolder(value) {
  if (typeof value !== "string") return "";
  const target = wslPath(value);
  return (target ? windowsPath(target.path, target) : value.replace(/\\/g, "/")).replace(/\/+$/, "");
}

// The shell text is fixed. Change names and all other arguments travel as argv.
const OPENSPEC = 'if [ -s "$HOME/.nvm/nvm.sh" ]; then . "$HOME/.nvm/nvm.sh" >/dev/null 2>&1; fi; tool=$(command -v openspec) || { printf "%s\\n" "Linux OpenSpec is not installed" >&2; exit 127; }; case "$tool" in /mnt/*) printf "%s\\n" "Linux OpenSpec is required; Windows npm shim was found" >&2; exit 127;; esac; exec "$tool" "$@"';

export async function exec(command, args = [], options = {}) {
  if (options.on || !["git", "openspec", "find", "env"].includes(command)) return nativeExec(command, args, options);
  const cwd = wslPath(options.cwd);
  const target = cwd || (command === "find" ? args.map(wslPath).find(Boolean) : null);
  if (!target) {
    // Windows folders: System32's find.exe isn't GNU find and there is no env.exe on
    // Herdr's PATH; use Git for Windows' own.
    if (/^[A-Za-z]:[\\/]/.test(home()) && (command === "find" || command === "env"))
      return nativeExec(`C:/Program Files/Git/usr/bin/${command}.exe`, args, options);
    return nativeExec(command, args, options);
  }
  const translated = command === "find" ? args.map(arg => {
    const path = wslPath(arg);
    if (!path) return arg;
    if (path.distro !== target.distro) throw new Error("A panel command cannot mix WSL distributions");
    return path.path;
  }) : args;
  const argv = ["-d", target.distro, "--cd", cwd?.path || "/", "--exec"];
  if (command === "openspec") argv.push("bash", "-lc", OPENSPEC, "herdr-openspec", ...translated);
  else argv.push(command, ...translated);
  const result = await nativeExec("wsl.exe", argv, { ...options, cwd: home(), on: null });
  if (result.code !== 0 && command !== "find") return result;
  let stdout = result.stdout;
  // Skip global Git options, including their values, before naming the operation.
  let operation = 0;
  while (args[operation]?.startsWith("-")) {
    operation += ["-c", "-C", "--git-dir", "--work-tree", "--namespace", "--config-env"].includes(args[operation]) ? 2 : 1;
  }
  if (command === "git" && args[operation] === "rev-parse" && (args.includes("--show-toplevel") || args.includes("--git-common-dir"))) {
    stdout = stdout.replace(/^\/[^\r\n]*/gm, line => windowsPath(line, target));
  } else if (command === "git" && args[operation] === "worktree" && args[operation + 1] === "list") {
    stdout = stdout.replace(/^worktree (\/[^\r\n]*)/gm, (_all, path) => `worktree ${windowsPath(path, target)}`);
  } else if (command === "find") {
    stdout = stdout.replace(/^\/[^\r\n]*/gm, line => windowsPath(line, target));
  }
  return { ...result, stdout };
}

export async function watchFolder(path) {
  if (wslPath(path)) throw new Error("Use the panel's existing poll timer for WSL folders");
  return nativeWatchFolder(path);
}
