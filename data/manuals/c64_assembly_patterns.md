# Pattern e Tecniche Classiche di Sviluppo 6502 su Commodore 64

## Aritmetica a 16 Bit con il 6502
Il 6502 è un microprocessore a 8 bit; le operazioni a 16 bit richiedono la propagazione esplicita del Carry Flag:

### Addizione a 16 Bit (num1 = num1 + num2)
```assembly
clc
lda num1_lo
adc num2_lo
sta num1_lo
lda num1_hi
adc num2_hi
sta num1_hi
```

### Sottrazione a 16 Bit (num1 = num1 - num2)
```assembly
sec            ; Nota: SEC prima di SBC (inverso di CLC prima di ADC)
lda num1_lo
sbc num2_lo
sta num1_lo
lda num1_hi
sbc num2_hi
sta num1_hi
```

## Attesa e Sincronizzazione Linea Raster ($D012)
Tecnica di polling per sincronizzare un effetto visivo con il pennello elettronico:
```assembly
wait_raster:
    lda $d012          ; Legge la riga raster corrente
    cmp #$80           ; Confronta con riga 128
    bne wait_raster    ; Attende che il raster raggiunga la linea
```

## Copia della Character ROM in RAM
Per ridefinire i caratteri mantenendo il font originale di fabbrica:
```assembly
sei                    ; Disabilita interrupt
lda $01
pha                    ; Salva configurazione banking
lda #$34               ; Espone la Char ROM a $D000-$DFFF
sta $01

; Copia 2048 byte da $D000 a $2000 (RAM)
ldx #$00
copy_loop:
    lda $d000,x
    sta $2000,x
    lda $d100,x
    sta $2100,x
    lda $d200,x
    sta $2200,x
    lda $d300,x
    sta $2300,x
    lda $d400,x
    sta $2400,x
    lda $d500,x
    sta $2500,x
    lda $d600,x
    sta $2600,x
    lda $d700,x
    sta $2700,x
    inx
    bne copy_loop

pla
sta $01                ; Ripristina configurazione originaria
cli                    ; Riabilita interrupt
rts
```

## Uscita Pulita da una Routine di Interrupt Personalizzata
Se il Kernal è attivo, si salta alla routine standard del Kernal:
```assembly
jmp $ea31              ; Conclude l'interrupt eseguendo scansione tastiera e orologio
; oppure jmp $ea81 per uscire senza eseguire le routine periodiche del Kernal
```
Se invece si lavora con ROM disattivate (full RAM), i registri salvati dalla CPU sullo stack devono essere ripristinati manualmente:
```assembly
pla
tay                    ; Ripristina Y
pla
tax                    ; Ripristina X
pla                    ; Ripristina A
rti                    ; Return from Interrupt (ripristina Status P e PC)
```
