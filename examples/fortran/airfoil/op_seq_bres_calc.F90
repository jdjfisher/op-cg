
! Auto-generated at 2021-01-19 15:09:18.002065 by opcg


MODULE BRES_CALC_MODULE

  USE OP2_FORTRAN_DECLARATIONS
  USE OP2_FORTRAN_RT_SUPPORT
  USE ISO_C_BINDING
  USE OP2_CONSTANTS

  CONTAINS

  ! Include kernel function
#include "bres_calc.inc"


  ! Wrapper for kernel function
  SUBROUTINE bres_calc_wrap ( & 
    & indDat_p_x, &
    & indDat_p_q, &
    & indDat_p_adt, &
    & indDat_p_res, &
    & dirDat_p_bound, &
    & map_pbedge, &
    & mapDim_pbedge, & 
    & map_pbecell, &
    & mapDim_pbecell, & 
    & bottom, &
    & top &
    & )

    IMPLICIT NONE

    real(8) indDat_p_x(2,*)
    real(8) indDat_p_q(4,*)
    real(8) indDat_p_adt(1,*)
    real(8) indDat_p_res(4,*)
    integer(4) dirDat_p_bound(1,*)

    INTEGER(kind=4) map_pbedge(*)
    INTEGER(kind=4) mapDim_pbedge
    INTEGER(kind=4) map_pbecell(*)
    INTEGER(kind=4) mapDim_pbecell
    INTEGER(kind=4) mapIdx_pbedge_0
    INTEGER(kind=4) mapIdx_pbedge_1
    INTEGER(kind=4) mapIdx_pbecell_0
    INTEGER(kind=4) mapIdx_pbecell_0
    INTEGER(kind=4) mapIdx_pbecell_0
    INTEGER(kind=4) bottom,top,i

    DO i = bottom, top - 1, 1 
      mapIdx_pbedge_0 = map_pbedge(1 + i * mapDim_pbedge + 0)+1 
      mapIdx_pbedge_1 = map_pbedge(1 + i * mapDim_pbedge + 1)+1 
      mapIdx_pbecell_0 = map_pbecell(1 + i * mapDim_pbecell + 0)+1 
      mapIdx_pbecell_0 = map_pbecell(1 + i * mapDim_pbecell + 0)+1 
      mapIdx_pbecell_0 = map_pbecell(1 + i * mapDim_pbecell + 0)+1

      ! Kernel call
      CALL bres_calc( &
        & indDat_p_x(1,mapIdx_pbedge_0), &
        & indDat_p_x(1,mapIdx_pbedge_1), &
        & indDat_p_q(1,mapIdx_pbecell_0), &
        & indDat_p_adt(1,mapIdx_pbecell_0), &
        & indDat_p_res(1,mapIdx_pbecell_0), &
        & dirDat_p_bound(1,i+1) &     
      & )

    END DO

  END SUBROUTINE



  ! Host function for kernel
  SUBROUTINE op_par_loop_bres_calc_host ( &
    & kernel, &
    & set, &
    & opArg1, &            
    & opArg2, &            
    & opArg3, &            
    & opArg4, &            
    & opArg5, &            
    & opArg6 &            
    & )

    IMPLICIT NONE
    character(kind=c_char,len=*), INTENT(IN) :: kernel
    type ( op_set ) , INTENT(IN) :: set

    type ( op_arg ) , INTENT(IN) :: opArg1
    type ( op_arg ) , INTENT(IN) :: opArg2
    type ( op_arg ) , INTENT(IN) :: opArg3
    type ( op_arg ) , INTENT(IN) :: opArg4
    type ( op_arg ) , INTENT(IN) :: opArg5
    type ( op_arg ) , INTENT(IN) :: opArg6

    type ( op_arg ) , DIMENSION(6) :: opArgArray
    INTEGER(kind=4) :: numberOfOpDats
    INTEGER(kind=4), DIMENSION(1:8) :: timeArrayStart
    INTEGER(kind=4), DIMENSION(1:8) :: timeArrayEnd
    REAL(kind=8) :: startTime
    REAL(kind=8) :: endTime
    INTEGER(kind=4) :: returnSetKernelTiming
    INTEGER(kind=4) :: n_upper
    type ( op_set_core ) , POINTER :: opSetCore


    real(8), POINTER, DIMENSION(:) :: indDat_p_x
    INTEGER(kind=4) :: indDatCard_p_x
    real(8), POINTER, DIMENSION(:) :: indDat_p_q
    INTEGER(kind=4) :: indDatCard_p_q
    real(8), POINTER, DIMENSION(:) :: indDat_p_adt
    INTEGER(kind=4) :: indDatCard_p_adt
    real(8), POINTER, DIMENSION(:) :: indDat_p_res
    INTEGER(kind=4) :: indDatCard_p_res
    integer(4), POINTER, DIMENSION(:) :: dirDat_p_bound
    INTEGER(kind=4) :: dirDatCard_p_bound
    INTEGER(kind=4), POINTER, DIMENSION(:) :: map_pbedge
    INTEGER(kind=4) :: mapDim_pbedge
    INTEGER(kind=4), POINTER, DIMENSION(:) :: map_pbecell
    INTEGER(kind=4) :: mapDim_pbecell

    INTEGER(kind=4) :: i
    REAL(kind=4) :: dataTransfer

    numberOfOpDats = 6

    opArgArray(1) = opArg1      
    opArgArray(2) = opArg2      
    opArgArray(3) = opArg3      
    opArgArray(4) = opArg4      
    opArgArray(5) = opArg5      
    opArgArray(6) = opArg6      

    returnSetKernelTiming = setKernelTime( &
      & 4, kernel//C_NULL_CHAR, &
      & 0.0_8, 0.00000_4,0.00000_4, 0 &
    & )
    CALL op_timers_core(startTime)

    n_upper = op_mpi_halo_exchanges(set%setCPtr,numberOfOpDats,opArgArray)

    opSetCore => set%setPtr

    indDatCard_p_x = opArg1%dim * getSetSizeFromOpArg(opArg1)
    indDatCard_p_q = opArg3%dim * getSetSizeFromOpArg(opArg3)
    indDatCard_p_adt = opArg4%dim * getSetSizeFromOpArg(opArg4)
    indDatCard_p_res = opArg5%dim * getSetSizeFromOpArg(opArg5)
    dirDatCard_p_bound = opArg6%dim * getSetSizeFromOpArg(opArg6)
    mapDim_pbedge = getMapDimFromOpArg(opArg1)
    mapDim_pbecell = getMapDimFromOpArg(opArg3)

    CALL c_f_pointer(opArg1%data, indDat_p_x, (/indDatCard_p_x/))
    CALL c_f_pointer(opArg1%map_data, map_pbedge, (/opSetCore%size*mapDim_pbedge/))
    CALL c_f_pointer(opArg3%data, indDat_p_q, (/indDatCard_p_q/))
    CALL c_f_pointer(opArg3%map_data, map_pbecell, (/opSetCore%size*mapDim_pbecell/))
    CALL c_f_pointer(opArg4%data, indDat_p_adt, (/indDatCard_p_adt/))
    CALL c_f_pointer(opArg4%map_data, map_pbecell, (/opSetCore%size*mapDim_pbecell/))
    CALL c_f_pointer(opArg5%data, indDat_p_res, (/indDatCard_p_res/))
    CALL c_f_pointer(opArg5%map_data, map_pbecell, (/opSetCore%size*mapDim_pbecell/))
    CALL c_f_pointer(opArg6%data, dirDat_p_bound, (/dirDatCard_p_bound/))


    CALL bres_calc_wrap( &
      & indDat_p_x, &
      & indDat_p_q, &
      & indDat_p_adt, &
      & indDat_p_res, &
      & dirDat_p_bound, &
      & map_pbedge, &
      & mapDim_pbedge, & 
      & map_pbecell, &
      & mapDim_pbecell, & 
      & 0, & 
      & opSetCore%core_size, & 
    & )

    CALL op_mpi_wait_all(numberOfOpDats, opArgArray)

    CALL bres_calc_wrap( &
      & indDat_p_x, &
      & indDat_p_q, &
      & indDat_p_adt, &
      & indDat_p_res, &
      & dirDat_p_bound, &
      & map_pbedge, &
      & mapDim_pbedge, & 
      & map_pbecell, &
      & mapDim_pbecell, & 
      & opSetCore%core_size, & 
      & n_upper &
    & )

    IF ((n_upper .EQ. 0) .OR. (n_upper .EQ. opSetCore%core_size)) THEN
      CALL op_mpi_wait_all(numberOfOpDats,opArgArray)
    END IF

    CALL op_mpi_set_dirtybit(numberOfOpDats,opArgArray)


    CALL op_timers_core(endTime)

    dataTransfer = 0.0

 
    dataTransfer = dataTransfer + opArg1%size * MIN(n_upper,getSetSizeFromOpArg(opArg1))
 
    dataTransfer = dataTransfer + opArg3%size * MIN(n_upper,getSetSizeFromOpArg(opArg3))
 
    dataTransfer = dataTransfer + opArg4%size * MIN(n_upper,getSetSizeFromOpArg(opArg4))
 
    dataTransfer = dataTransfer + opArg5%size * MIN(n_upper,getSetSizeFromOpArg(opArg5)) * 2.d0
 
    dataTransfer = dataTransfer + opArg6%size * MIN(n_upper,getSetSizeFromOpArg(opArg6))
    dataTransfer = dataTransfer + n_upper * mapDim_pbedge * 4.d0
    dataTransfer = dataTransfer + n_upper * mapDim_pbecell * 4.d0

    returnSetKernelTiming = setKernelTime( &
      & 4, kernel//C_NULL_CHAR, &
      & endTime-startTime, dataTransfer, 0.00000_4, 1 &
    & )
  END SUBROUTINE

END MODULE



