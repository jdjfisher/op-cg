
! Auto-generated at 2021-01-19 14:05:55.579226 by opcg


MODULE ADT_CALC_1_MODULE

  USE OP2_FORTRAN_DECLARATIONS
  USE OP2_FORTRAN_RT_SUPPORT
  USE ISO_C_BINDING
  USE OP2_CONSTANTS

  CONTAINS

  ! Include kernel function
  #include "adt_calc.inc"


  ! Wrapper for kernel function
  SUBROUTINE adt_calc_1_wrap ( & 
    & indDat_pcell_p_x, &
    & dirDat_p_q, &
    & dirDat_p_adt, &
    & map_pcell, &
    & mapDim_pcell, & 
    & bottom, &
    & top &
    & )

    IMPLICIT NONE

    real(8) indDat_pcell_p_x(2,*)
    real(8) dirDat_p_q(4,*)
    real(8) dirDat_p_adt(1,*)

    INTEGER(kind=4) map_pcell(*)
    INTEGER(kind=4) mapDim_pcell
    INTEGER(kind=4) mapIdx_pcell_0
    INTEGER(kind=4) mapIdx_pcell_1
    INTEGER(kind=4) mapIdx_pcell_2
    INTEGER(kind=4) mapIdx_pcell_3
    INTEGER(kind=4) bottom,top,i1

    DO i = bottom, top - 1, 1 
      mapIdx_pcell_0 = map_pcell(1 + i * mapDim_pcell + 0)+1 
      mapIdx_pcell_1 = map_pcell(1 + i * mapDim_pcell + 1)+1 
      mapIdx_pcell_2 = map_pcell(1 + i * mapDim_pcell + 2)+1 
      mapIdx_pcell_3 = map_pcell(1 + i * mapDim_pcell + 3)+1

      ! Kernel call
      CALL adt_calc( &
        & indDat_p_x(1,mapIdx_pcell_0), &
        & indDat_p_x(1,mapIdx_pcell_1), &
        & indDat_p_x(1,mapIdx_pcell_2), &
        & indDat_p_x(1,mapIdx_pcell_3), &
        & dirDat_p_q(1,i+1), &     
        & dirDat_p_adt(1,i+1) &     
      & )

    END DO

  END SUBROUTINE



  ! Host function for kernel
  SUBROUTINE op_par_loop_adt_calc_1_host ( &
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
    character(kind=c_char,len=*), INTENT(IN) :: userSubroutine
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
    INTEGER(kind=4) :: indDatCard_pcell_p_x
    real(8), POINTER, DIMENSION(:) :: dirDat_p_q
    INTEGER(kind=4) :: dirDatCard_p_q
    real(8), POINTER, DIMENSION(:) :: dirDat_p_adt
    INTEGER(kind=4) :: dirDatCard_p_adt
    INTEGER(kind=4), POINTER, DIMENSION(:) :: map_pcell
    INTEGER(kind=4) :: mapDim_pcell

    INTEGER(kind=4) :: i1
    REAL(kind=4) :: dataTransfer

    numberOfOpDats = 6

    opArgArray(1) = opArg1      
    opArgArray(2) = opArg2      
    opArgArray(3) = opArg3      
    opArgArray(4) = opArg4      
    opArgArray(5) = opArg5      
    opArgArray(6) = opArg6      

    returnSetKernelTiming = setKernelTime( &
      & 2, userSubroutine//C_NULL_CHAR, &
      & 0.0_8, 0.00000_4,0.00000_4, 0 &
    & )
    CALL op_timers_core(startTime)

    n_upper = op_mpi_halo_exchanges(set%setCPtr,numberOfOpDats,opArgArray)

    opSetCore => set%setPtr

    indDatCard_pcell_p_x = opArg1%dim * getSetSizeFromOpArg(opArg1)
    dirDatCard_p_q = opArg5%dim * getSetSizeFromOpArg(opArg5)
    dirDatCard_p_adt = opArg6%dim * getSetSizeFromOpArg(opArg6)
    mapDim_pcell = getMapDimFromOpArg(opArg1)

    CALL c_f_pointer(opArg1%data, indDat_pcell_p_x, (/indDatCard_pcell_p_x/))
    CALL c_f_pointer(opArg1%map_data, map_pcell, (/opSetCore%size*mapDim_pcell/))
    CALL c_f_pointer(opArg5%data, dirDat_p_q, (/dirDatCard_p_q/))
    CALL c_f_pointer(opArg6%data, dirDat_p_adt, (/dirDatCard_p_adt/))


    CALL adt_calc_1_wrap( &
      & indDat_pcell_p_x, &
      & dirDat_p_q, &
      & dirDat_p_adt, &
      & map_pcell, &
      & mapDim_pcell, & 
      & 0, & 
      & opSetCore%core_size, & 
    & )

    CALL op_mpi_wait_all(numberOfOpDats, opArgArray)

    CALL adt_calc_1_wrap( &
      & indDat_pcell_p_x, &
      & dirDat_p_q, &
      & dirDat_p_adt, &
      & map_pcell, &
      & mapDim_pcell, & 
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
 
    dataTransfer = dataTransfer + opArg5%size * MIN(n_upper,getSetSizeFromOpArg(opArg5))
 
    dataTransfer = dataTransfer + opArg6%size * MIN(n_upper,getSetSizeFromOpArg(opArg6))
    dataTransfer = dataTransfer + n_upper * mapDim_pcell * 4.d0

    returnSetKernelTiming = setKernelTime( &
      & 2, kernel//C_NULL_CHAR, &
      & endTime-startTime, dataTransfer, 0.00000_4, 1 &
    & )
  END SUBROUTINE

END MODULE



