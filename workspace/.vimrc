" Vimtut Tutorial Configuration
" This config is loaded during tutorial sessions

" Show line numbers
set number

" Highlight current line
set cursorline

" Enable syntax highlighting
syntax on

" Disable alternate screen buffer switching
" The app manages the alternate screen, so Vim stays in the same buffer
set t_ti= t_te=

" Set status line to show lesson info
set laststatus=2
set statusline=\ VIMTUT\ \|\ Press\ ESC\ then\ :wq\ to\ save\ and\ quit

" Show the current mode (INSERT, VISUAL, etc.)
set showmode

" Make backspace work as expected in insert mode
set backspace=indent,eol,start

" Indentation settings (for shift lesson)
set shiftwidth=4
set expandtab

" Reduce startup messages
set shortmess+=I    " Don't show intro message
set shortmess+=F    " Don't show file info when editing

" Create split view with instructions on startup
augroup VimtutSetup
  autocmd!
  autocmd VimEnter * call SetupVimtut()
augroup END

" Intercept all quit commands and quit all windows instead
let g:vimtut_quitting = 0

function! VimtutQuitHandler()
  if g:vimtut_quitting
    return
  endif
  let g:vimtut_quitting = 1
  qall!
endfunction

augroup VimtutQuit
  autocmd!
  autocmd QuitPre * call VimtutQuitHandler()
augroup END

function! SetupVimtut()
  " Save the current file name (the task file)
  let l:task_file = expand('%:p')
  let l:instructions_file = expand('%:p:h') . '/instructions.txt'

  " Check if instructions file exists
  if filereadable(l:instructions_file)
    " Create horizontal split with instructions at bottom
    " Use silent! to suppress file info messages
    silent! execute 'belowright split ' . l:instructions_file

    " Make instructions window large enough to show content (most lessons need 20-28 lines)
    resize 25

    " Make it read-only
    setlocal readonly
    setlocal nomodifiable

    " Disable line numbers in instructions pane
    setlocal nonumber

    " Disable cursor line in instructions
    setlocal nocursorline

    " Enable word wrapping for long lines
    setlocal wrap
    setlocal linebreak

    " Add syntax highlighting for instructions
    syntax clear
    syntax match VimtutHeader /^LESSON:.*$/
    syntax match VimtutSeparator /^=\+$/
    syntax match VimtutTask /Your task:.*$/
    syntax match VimtutSteps /^Steps:$/
    syntax match VimtutStepNum /^\d\+\./
    syntax match VimtutQuote /'/
    syntax match VimtutKeyCmd /'\@<=[^']\+'\@=/
    syntax match VimtutWarning /Note:.*$/
    syntax match VimtutTip /Tip:.*$/

    " Define colors for instruction elements
    highlight VimtutHeader ctermfg=Cyan cterm=bold guifg=#00FFFF gui=bold
    highlight VimtutSeparator ctermfg=DarkGray guifg=#666666
    highlight VimtutTask ctermfg=Yellow cterm=bold guifg=#FFFF00 gui=bold
    highlight VimtutSteps ctermfg=Green cterm=bold guifg=#00FF00 gui=bold
    highlight VimtutStepNum ctermfg=Magenta guifg=#FF00FF
    highlight VimtutQuote ctermfg=DarkGray guifg=#888888
    highlight VimtutKeyCmd ctermfg=Green cterm=bold guifg=#00FF00 gui=bold
    highlight VimtutWarning ctermfg=Red guifg=#FF6666
    highlight VimtutTip ctermfg=Cyan guifg=#66FFFF

    " Set a different status line for instructions
    setlocal statusline=\ INSTRUCTIONS\ (Read-Only)\ -\ Scroll\ with\ Ctrl+j\ then\ j/k

    " Move back to the top window (task file)
    wincmd k

    " Focus on the task file
    " Go to first line
    normal! gg

    " Redraw to ensure clean display
    redraw!

  endif
endfunction

" Key mappings for easier window navigation (optional)
" Ctrl+j and Ctrl+k to move between splits
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
