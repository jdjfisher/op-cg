
! Auto-generated at 2021-01-19 14:51:29.697764 by opcg


MODULE RES_CALC_MODULE

  USE OP2_FORTRAN_DECLARATIONS
  USE OP2_FORTRAN_RT_SUPPORT
  USE ISO_C_BINDING
  USE OP2_CONSTANTS

  CONTAINS

  ! Include kernel function
#include "res_calc.inc"


  ! Wrapper for kernel function
  SUBROUTINE res_calc_wrap ( & 
    & indDat_pedge_p_x, &
    & indDat_pecell_p_q, &
    & indDat_pecell_p_adt, &
    & indDat_pecell_p_res, &
    & map_pedge, &
    & mapDim_pedge, & 
    & map_pecell, &
    & mapDim_pecell, & 
    & bottom, &
    & top &
    & )

    IMPLICIT NONE

    real(8) indDat_pedge_p_x(2,*)
    real(8) indDat_pecell_p_q(4,*)
    real(8) indDat_pecell_p_adt(1,*)
    real(8) indDat_pecell_p_res(4,*)

    INTEGER(kind=4) map_pedge(*)
    INTEGER(kind=4) mapDim_pedge
    INTEGER(kind=4) map_pecell(*)
    INTEGER(kind=4) mapDim_pecell
    INTEGER(kind=4) mapIdx_pedge_0
    INTEGER(kind=4) mapIdx_pedge_1
    INTEGER(kind=4) mapIdx_pecell_0
    INTEGER(kind=4) mapIdx_pecell_1
    INTEGER(kind=4) mapIdx_pecell_0
    INTEGER(kind=4) mapIdx_pecell_1
    INTEGER(kind=4) mapIdx_pecell_0
    INTEGER(kind=4) mapIdx_pecell_1
    INTEGER(kind=4) bottom,top,i

    DO i = bottom, top - 1, 1 
      mapIdx_pedge_0 = map_pedge(1 + i * mapDim_pedge + 0)+1 
      mapIdx_pedge_1 = map_pedge(1 + i * mapDim_pedge + 1)+1 
      mapIdx_pecell_0 = map_pecell(1 + i * mapDim_pecell + 0)+1 
      mapIdx_pecell_1 = map_pecell(1 + i * mapDim_pecell + 1)+1 
      mapIdx_pecell_0 = map_pecell(1 + i * mapDim_pecell + 0)+1 
      mapIdx_pecell_1 = map_pecell(1 + i * mapDim_pecell + 1)+1 
      mapIdx_pecell_0 = map_pecell(1 + i * mapDim_pecell + 0)+1 
      mapIdx_pecell_1 = map_pecell(1 + i * mapDim_pecell + 1)+1

      ! Kernel call
      CALL res_calc( &
        & indDat_p_x(1,mapIdx_pedge_0), &
        & indDat_p_x(1,mapIdx_pedge_1), &
        & indDat_p_q(1,mapIdx_pecell_0), &
        & indDat_p_q(1,mapIdx_pecell_1), &
        & indDat_p_adt(1,mapIdx_pecell_0), &
        & indDat_p_adt(1,mapIdx_pecell_1), &
        & indDat_p_res(1,mapIdx_pecell_0), &
        & indDat_p_res(1,mapIdx_pecell_1) &
      & )

    END DO

  END SUBROUTINE



  ! Host function for kernel
  SUBROUTINE op_par_loop_res_calc_host ( &
    & kernel, &
    & set, &
    & opArg1, &            
    & opArg2, &            
    & opArg3, &            
    & opArg4, &            
    & opArg5, &            
    & opArg6, &            
    & opArg7, &            
    & opArg8 &            
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
    type ( op_arg ) , INTENT(IN) :: opArg7
    type ( op_arg ) , INTENT(IN) :: opArg8

    type ( op_arg ) , DIMENSION(8) :: opArgArray
    INTEGER(kind=4) :: numberOfOpDats
    INTEGER(kind=4), DIMENSION(1:8) :: timeArrayStart
    INTEGER(kind=4), DIMENSION(1:8) :: timeArrayEnd
    REAL(kind=8) :: startTime
    REAL(kind=8) :: endTime
    INTEGER(kind=4) :: returnSetKernelTiming
    INTEGER(kind=4) :: n_upper
    type ( op_set_core ) , POINTER :: opSetCore


    real(8), POINTER, DIMENSION(:) :: indDat_p_x
    INTEGER(kind=4) :: indDatCard_pedge_p_x
    real(8), POINTER, DIMENSION(:) :: indDat_p_q
    INTEGER(kind=4) :: indDatCard_pecell_p_q
    real(8), POINTER, DIMENSION(:) :: indDat_p_adt
    INTEGER(kind=4) :: indDatCard_pecell_p_adt
    real(8), POINTER, DIMENSION(:) :: indDat_p_res
    INTEGER(kind=4) :: indDatCard_pecell_p_res
    INTEGER(kind=4), POINTER, DIMENSION(:) :: map_pedge
    INTEGER(kind=4) :: mapDim_pedge
    INTEGER(kind=4), POINTER, DIMENSION(:) :: map_pecell
    INTEGER(kind=4) :: mapDim_pecell

    INTEGER(kind=4) :: i
    REAL(kind=4) :: dataTransfer

    numberOfOpDats = 8

    opArgArray(1) = opArg1      
    opArgArray(2) = opArg2      
    opArgArray(3) = opArg3      
    opArgArray(4) = opArg4      
    opArgArray(5) = opArg5      
    opArgArray(6) = opArg6      
    opArgArray(7) = opArg7      
    opArgArray(8) = opArg8      

    returnSetKernelTiming = setKernelTime( &
      & 3, kernel//C_NULL_CHAR, &
      & 0.0_8, 0.00000_4,0.00000_4, 0 &
    & )
    CALL op_timers_core(startTime)

    n_upper = op_mpi_halo_exchanges(set%setCPtr,numberOfOpDats,opArgArray)

    opSetCore => set%setPtr

    indDatCard_pedge_p_x = opArg1%dim * getSetSizeFromOpArg(opArg1)
    indDatCard_pecell_p_q = opArg3%dim * getSetSizeFromOpArg(opArg3)
    indDatCard_pecell_p_adt = opArg5%dim * getSetSizeFromOpArg(opArg5)
    indDatCard_pecell_p_res = opArg7%dim * getSetSizeFromOpArg(opArg7)
    mapDim_pedge = getMapDimFromOpArg(opArg1)
    mapDim_pecell = getMapDimFromOpArg(opArg3)

    CALL c_f_pointer(opArg1%data, indDat_pedge_p_x, (/indDatCard_pedge_p_x/))
    CALL c_f_pointer(opArg1%map_data, map_pedge, (/opSetCore%size*mapDim_pedge/))
    CALL c_f_pointer(opArg3%data, indDat_pecell_p_q, (/indDatCard_pecell_p_q/))
    CALL c_f_pointer(opArg3%map_data, map_pecell, (/opSetCore%size*mapDim_pecell/))
    CALL c_f_pointer(opArg5%data, indDat_pecell_p_adt, (/indDatCard_pecell_p_adt/))
    CALL c_f_pointer(opArg5%map_data, map_pecell, (/opSetCore%size*mapDim_pecell/))
    CALL c_f_pointer(opArg7%data, indDat_pecell_p_res, (/indDatCard_pecell_p_res/))
    CALL c_f_pointer(opArg7%map_data, map_pecell, (/opSetCore%size*mapDim_pecell/))


    CALL res_calc_wrap( &
      & indDat_pedge_p_x, &
      & indDat_pecell_p_q, &
      & indDat_pecell_p_adt, &
      & indDat_pecell_p_res, &
      & map_pedge, &
      & mapDim_pedge, & 
      & map_pecell, &
      & mapDim_pecell, & 
      & 0, & 
      & opSetCore%core_size, & 
    & )

    CALL op_mpi_wait_all(numberOfOpDats, opArgArray)

    CALL res_calc_wrap( &
      & indDat_pedge_p_x, &
      & indDat_pecell_p_q, &
      & indDat_pecell_p_adt, &
      & indDat_pecell_p_res, &
      & map_pedge, &
      & mapDim_pedge, & 
      & map_pecell, &
      & mapDim_pecell, & 
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
 
    dataTransfer = dataTransfer + opArg5%size * MIN(n_upper,getSetSizeFromOpArg(opArg5))
 
    dataTransfer = dataTransfer + opArg7%size * MIN(n_upper,getSetSizeFromOpArg(opArg7)) * 2.d0
    dataTransfer = dataTransfer + n_upper * mapDim_pedge * 4.d0
    dataTransfer = dataTransfer + n_upper * mapDim_pecell * 4.d0

    returnSetKernelTiming = setKernelTime( &
      & 3, kernel//C_NULL_CHAR, &
      & endTime-startTime, dataTransfer, 0.00000_4, 1 &
    & )
  END SUBROUTINE

END MODULE



