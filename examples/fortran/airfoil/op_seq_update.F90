
! Auto-generated at 2021-01-19 14:51:29.698466 by opcg


MODULE UPDATE_MODULE

  USE OP2_FORTRAN_DECLARATIONS
  USE OP2_FORTRAN_RT_SUPPORT
  USE ISO_C_BINDING
  USE OP2_CONSTANTS

  CONTAINS

  ! Include kernel function
#include "update.inc"


  ! Wrapper for kernel function
  SUBROUTINE update_wrap ( & 
    & dirDat_p_qold, &
    & dirDat_p_q, &
    & dirDat_p_res, &
    & dirDat_p_adt, &
    & gblDat_rms, &
    & bottom, &
    & top &
    & )

    IMPLICIT NONE

    real(8) dirDat_p_qold(4,*)
    real(8) dirDat_p_q(4,*)
    real(8) dirDat_p_res(4,*)
    real(8) dirDat_p_adt(1,*)
    real(8) gblDat_rms(2,*)

    INTEGER(kind=4) bottom,top,i

    DO i = bottom, top - 1, 1

      ! Kernel call
      CALL update( &
        & dirDat_p_qold(1,i+1), &     
        & dirDat_p_q(1,i+1), &     
        & dirDat_p_res(1,i+1), &     
        & dirDat_p_adt(1,i+1), &     
        & gblDat_rms(1) &     
      & )

    END DO

  END SUBROUTINE



  ! Host function for kernel
  SUBROUTINE op_par_loop_update_host ( &
    & kernel, &
    & set, &
    & opArg1, &            
    & opArg2, &            
    & opArg3, &            
    & opArg4, &            
    & opArg5 &            
    & )

    IMPLICIT NONE
    character(kind=c_char,len=*), INTENT(IN) :: kernel
    type ( op_set ) , INTENT(IN) :: set

    type ( op_arg ) , INTENT(IN) :: opArg1
    type ( op_arg ) , INTENT(IN) :: opArg2
    type ( op_arg ) , INTENT(IN) :: opArg3
    type ( op_arg ) , INTENT(IN) :: opArg4
    type ( op_arg ) , INTENT(IN) :: opArg5

    type ( op_arg ) , DIMENSION(5) :: opArgArray
    INTEGER(kind=4) :: numberOfOpDats
    INTEGER(kind=4), DIMENSION(1:8) :: timeArrayStart
    INTEGER(kind=4), DIMENSION(1:8) :: timeArrayEnd
    REAL(kind=8) :: startTime
    REAL(kind=8) :: endTime
    INTEGER(kind=4) :: returnSetKernelTiming
    INTEGER(kind=4) :: n_upper
    type ( op_set_core ) , POINTER :: opSetCore


    real(8), POINTER, DIMENSION(:) :: dirDat_p_qold
    INTEGER(kind=4) :: dirDatCard_p_qold
    real(8), POINTER, DIMENSION(:) :: dirDat_p_q
    INTEGER(kind=4) :: dirDatCard_p_q
    real(8), POINTER, DIMENSION(:) :: dirDat_p_res
    INTEGER(kind=4) :: dirDatCard_p_res
    real(8), POINTER, DIMENSION(:) :: dirDat_p_adt
    INTEGER(kind=4) :: dirDatCard_p_adt
    real(8), POINTER, DIMENSION(:) :: gblDat_rms

    INTEGER(kind=4) :: i
    REAL(kind=4) :: dataTransfer

    numberOfOpDats = 5

    opArgArray(1) = opArg1      
    opArgArray(2) = opArg2      
    opArgArray(3) = opArg3      
    opArgArray(4) = opArg4      
    opArgArray(5) = opArg5      

    returnSetKernelTiming = setKernelTime( &
      & 5, kernel//C_NULL_CHAR, &
      & 0.0_8, 0.00000_4,0.00000_4, 0 &
    & )
    CALL op_timers_core(startTime)

    n_upper = op_mpi_halo_exchanges(set%setCPtr,numberOfOpDats,opArgArray)

    opSetCore => set%setPtr

    dirDatCard_p_qold = opArg1%dim * getSetSizeFromOpArg(opArg1)
    dirDatCard_p_q = opArg2%dim * getSetSizeFromOpArg(opArg2)
    dirDatCard_p_res = opArg3%dim * getSetSizeFromOpArg(opArg3)
    dirDatCard_p_adt = opArg4%dim * getSetSizeFromOpArg(opArg4)

    CALL c_f_pointer(opArg1%data, dirDat_p_qold, (/dirDatCard_p_qold/))
    CALL c_f_pointer(opArg2%data, dirDat_p_q, (/dirDatCard_p_q/))
    CALL c_f_pointer(opArg3%data, dirDat_p_res, (/dirDatCard_p_res/))
    CALL c_f_pointer(opArg4%data, dirDat_p_adt, (/dirDatCard_p_adt/))
    CALL c_f_pointer(opArg5%data, gblDat_rms, (/opArg5%dim/))


    CALL update_wrap( &
      & dirDat_p_qold, &
      & dirDat_p_q, &
      & dirDat_p_res, &
      & dirDat_p_adt, &
      & gblDat_rms, &
      & 0, & 
      & opSetCore%core_size, & 
    & )

    CALL op_mpi_wait_all(numberOfOpDats, opArgArray)

    CALL update_wrap( &
      & dirDat_p_qold, &
      & dirDat_p_q, &
      & dirDat_p_res, &
      & dirDat_p_adt, &
      & gblDat_rms, &
      & opSetCore%core_size, & 
      & n_upper &
    & )

    IF ((n_upper .EQ. 0) .OR. (n_upper .EQ. opSetCore%core_size)) THEN
      CALL op_mpi_wait_all(numberOfOpDats,opArgArray)
    END IF

    CALL op_mpi_set_dirtybit(numberOfOpDats,opArgArray)

 
 
    CALL op_mpi_reduce_double(opArg5, opArg5%data)


    CALL op_timers_core(endTime)

    dataTransfer = 0.0

   
    dataTransfer = dataTransfer + opArg1%size * opSetCore%size
   
    dataTransfer = dataTransfer + opArg2%size * opSetCore%size
   
    dataTransfer = dataTransfer + opArg3%size * opSetCore%size * 2.d0
   
    dataTransfer = dataTransfer + opArg4%size * opSetCore%size
   
    dataTransfer = dataTransfer + opArg5%size * 2.d0

    returnSetKernelTiming = setKernelTime( &
      & 5, kernel//C_NULL_CHAR, &
      & endTime-startTime, dataTransfer, 0.00000_4, 1 &
    & )
  END SUBROUTINE

END MODULE



