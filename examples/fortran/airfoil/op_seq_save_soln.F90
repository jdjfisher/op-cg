
! Auto-generated at 2021-01-20 19:24:35.206890 by opcg


MODULE SAVE_SOLN_MODULE

  USE OP2_FORTRAN_DECLARATIONS
  USE OP2_FORTRAN_RT_SUPPORT
  USE ISO_C_BINDING
  USE OP2_CONSTANTS

  CONTAINS

  ! Include kernel function
#include "save_soln.inc"


  ! Wrapper for kernel function
  SUBROUTINE save_soln_wrap ( & 
    & dirDat_p_q, &
    & dirDat_p_qold, &
    & bottom, &
    & top &
    & )

    IMPLICIT NONE

    real(8) dirDat_p_q(4,*)
    real(8) dirDat_p_qold(4,*)

    INTEGER(kind=4) bottom,top,i

    DO i = bottom, top - 1, 1

      ! Kernel call
      CALL save_soln( &
        & dirDat_p_q(1,i+1), &     
        & dirDat_p_qold(1,i+1) &     
      & )

    END DO

  END SUBROUTINE



  ! Host function for kernel
  SUBROUTINE op_par_loop_save_soln_host ( &
    & kernel, &
    & set, &
    & opArg1, &            
    & opArg2 &            
    & )

    IMPLICIT NONE
    character(kind=c_char,len=*), INTENT(IN) :: kernel
    type ( op_set ) , INTENT(IN) :: set

    type ( op_arg ) , INTENT(IN) :: opArg1
    type ( op_arg ) , INTENT(IN) :: opArg2

    type ( op_arg ) , DIMENSION(2) :: opArgArray
    INTEGER(kind=4) :: numberOfOpDats
    INTEGER(kind=4), DIMENSION(1:8) :: timeArrayStart
    INTEGER(kind=4), DIMENSION(1:8) :: timeArrayEnd
    REAL(kind=8) :: startTime
    REAL(kind=8) :: endTime
    INTEGER(kind=4) :: returnSetKernelTiming
    INTEGER(kind=4) :: n_upper
    type ( op_set_core ) , POINTER :: opSetCore


    real(8), POINTER, DIMENSION(:) :: dirDat_p_q
    INTEGER(kind=4) :: dirDatCard_p_q
    real(8), POINTER, DIMENSION(:) :: dirDat_p_qold
    INTEGER(kind=4) :: dirDatCard_p_qold

    INTEGER(kind=4) :: i
    REAL(kind=4) :: dataTransfer

    numberOfOpDats = 2

    opArgArray(1) = opArg1      
    opArgArray(2) = opArg2      

    returnSetKernelTiming = setKernelTime( &
      & 1, kernel//C_NULL_CHAR, &
      & 0.0_8, 0.00000_4,0.00000_4, 0 &
    & )
    CALL op_timers_core(startTime)

    n_upper = op_mpi_halo_exchanges(set%setCPtr,numberOfOpDats,opArgArray)

    opSetCore => set%setPtr

    dirDatCard_p_q = opArg1%dim * getSetSizeFromOpArg(opArg1)
    dirDatCard_p_qold = opArg2%dim * getSetSizeFromOpArg(opArg2)

    CALL c_f_pointer(opArg1%data, dirDat_p_q, (/dirDatCard_p_q/))
    CALL c_f_pointer(opArg2%data, dirDat_p_qold, (/dirDatCard_p_qold/))


    CALL save_soln_wrap( &
      & dirDat_p_q, &
      & dirDat_p_qold, &
      & 0, & 
      & opSetCore%core_size & 
    & )

    CALL op_mpi_wait_all(numberOfOpDats, opArgArray)

    CALL save_soln_wrap( &
      & dirDat_p_q, &
      & dirDat_p_qold, &
      & opSetCore%core_size, & 
      & n_upper &
    & )

    IF ((n_upper .EQ. 0) .OR. (n_upper .EQ. opSetCore%core_size)) THEN
      CALL op_mpi_wait_all(numberOfOpDats,opArgArray)
    END IF

    CALL op_mpi_set_dirtybit(numberOfOpDats,opArgArray)


    CALL op_timers_core(endTime)

    dataTransfer = 0.0

   
    dataTransfer = dataTransfer + opArg1%size * opSetCore%size
   
    dataTransfer = dataTransfer + opArg2%size * opSetCore%size

    returnSetKernelTiming = setKernelTime( &
      & 1, kernel//C_NULL_CHAR, &
      & endTime-startTime, dataTransfer, 0.00000_4, 1 &
    & )
  END SUBROUTINE

END MODULE