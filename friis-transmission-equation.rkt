#lang racket

(define (dBm->mW dBm-val)
  (expt 10 (/ dBm-val 10)))

(define (dBm->W dBm-val)
  (expt 10 (- (/ dBm-val 10) 3)))

;(define U 5)
;(define I 0.02)
;(define P_t (* U I))
(define P_t (dBm->W 10)) ;; From datasheet
(define wave-freq 433e6)
(define G_t 1.64)
(define G_r 1.0)



(define (P_r wave-freq
             P_t
             distance
             #:G_t [G_t 1.0]
             #:G_r [G_r 1.0]
             #:v [v 3e8])
    (* P_t (* G_t (* G_r (/ (/ v wave-freq) (expt (* 4 (* pi distance)) 2))))))


(display (format "Antenna power: ~a [W] \n40 meters dipole: ~a\n40 meters yagi-uda: ~a\n400 meters dipole: ~a\n400 meters yagi-uda: ~a\n"
                 (exact->inexact P_t)
                 (P_r wave-freq P_t 40 #:G_t 1.64)
                 (P_r wave-freq P_t 40 #:G_t 10)
                 (P_r wave-freq P_t 400 #:G_t 1.64)
                 (P_r wave-freq P_t 400 #:G_t 10)))
