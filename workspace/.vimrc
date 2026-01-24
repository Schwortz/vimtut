" Vim Dojo Tutorial Configuration
" This config is loaded during tutorial sessions

" Show line numbers
set number

" Highlight current line
set cursorline

" Enable syntax highlighting
syntax on

" Set status line to show lesson info
set laststatus=2
set statusline=\ VIM\ DOJO\ \|\ Press\ ESC\ then\ :wq\ to\ save\ and\ quit

" Show the current mode (INSERT, VISUAL, etc.)
set showmode

" Make backspace work as expected in insert mode
set backspace=indent,eol,start

" Reduce startup messages
set shortmess+=I    " Don't show intro message
set shortmess+=F    " Don't show file info when editing

" Create split view with instructions on startup
augroup VimDojoSetup
  autocmd!
  autocmd VimEnter * call SetupVimDojo()
augroup END

function! DojoQuit(save)
  " Custom quit function for Vim Dojo
  " a:save = 1 means save before quit (:wq), 0 means just quit (:q)
  if a:save
    " Save current file first
    write
  endif
  " Then quit all windows
  qall
endfunction

function! SetupVimDojo()
  " Save the current file name (the task file)
  let l:task_file = expand('%:p')
  let l:instructions_file = expand('%:p:h') . '/instructions.txt'

  " Check if instructions file exists
  if filereadable(l:instructions_file)
    " Create horizontal split with instructions at bottom
    " Use silent! to suppress file info messages
    silent! execute 'belowright split ' . l:instructions_file

    " Make instructions window smaller (about 1/3 of screen)
    resize 12

    " Make it read-only
    setlocal readonly
    setlocal nomodifiable

    " Disable line numbers in instructions pane
    setlocal nonumber

    " Disable cursor line in instructions
    setlocal nocursorline

    " Set a different status line for instructions
    setlocal statusline=\ INSTRUCTIONS\ (Read-Only)

    " Move back to the top window (task file)
    wincmd k

    " Focus on the task file
    " Go to first line
    normal! gg

    " Redraw to ensure clean display
    redraw!

    " Remap :q and :wq to close all windows
    " :wq saves current file then quits all
    " :q just quits all
    cnoreabbrev <expr> q getcmdtype() == ':' && getcmdline() == 'q' ? 'call DojoQuit(0)' : 'q'
    cnoreabbrev <expr> wq getcmdtype() == ':' && getcmdline() == 'wq' ? 'call DojoQuit(1)' : 'wq'
    cnoreabbrev <expr> x getcmdtype() == ':' && getcmdline() == 'x' ? 'call DojoQuit(1)' : 'x'
  endif
endfunction

" Key mappings for easier window navigation (optional)
" Ctrl+j and Ctrl+k to move between splits
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
